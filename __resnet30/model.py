from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import numpy as np
import time
import logging
import json

import paddle
import paddle.fluid as fluid
import paddle.fluid.core as core
from continuous_evaluation import *

logger = logging.getLogger(__name__)


# model configs
def conv_bn_layer(input, ch_out, filter_size, stride, padding, act='relu'):
    conv1 = fluid.layers.conv2d(
        input=input,
        filter_size=filter_size,
        num_filters=ch_out,
        stride=stride,
        padding=padding,
        act=None,
        bias_attr=False)
    return fluid.layers.batch_norm(input=conv1, act=act)


def shortcut(input, ch_out, stride):
    ch_in = input.shape[1]
    if ch_in != ch_out:
        return conv_bn_layer(input, ch_out, 1, stride, 0, None)
    else:
        return input


def basicblock(input, ch_out, stride):
    short = shortcut(input, ch_out, stride)
    conv1 = conv_bn_layer(input, ch_out, 3, stride, 1)
    conv2 = conv_bn_layer(conv1, ch_out, 3, 1, 1, act=None)
    return fluid.layers.elementwise_add(x=short, y=conv2, act='relu')


def bottleneck(input, ch_out, stride):
    short = shortcut(input, ch_out * 4, stride)
    conv1 = conv_bn_layer(input, ch_out, 1, stride, 0)
    conv2 = conv_bn_layer(conv1, ch_out, 3, 1, 1)
    conv3 = conv_bn_layer(conv2, ch_out * 4, 1, 1, 0, act=None)
    return fluid.layers.elementwise_add(x=short, y=conv3, act='relu')


def layer_warp(block_func, input, ch_out, count, stride):
    res_out = block_func(input, ch_out, stride)
    for i in range(1, count):
        res_out = block_func(res_out, ch_out, 1)
    return res_out


def resnet_cifar10(input, class_dim, depth=32):
    assert (depth - 2) % 6 == 0

    n = (depth - 2) // 6

    conv1 = conv_bn_layer(
        input=input, ch_out=16, filter_size=3, stride=1, padding=1)
    res1 = layer_warp(basicblock, conv1, 16, n, 1)
    res2 = layer_warp(basicblock, res1, 32, n, 2)
    res3 = layer_warp(basicblock, res2, 64, n, 2)
    pool = fluid.layers.pool2d(
        input=res3, pool_size=8, pool_type='avg', pool_stride=1)
    out = fluid.layers.fc(input=pool, size=class_dim, act='softmax')
    return out


def train(batch_size, device, pass_num, iterations):
    print('iterations', iterations)
    class_dim = 10
    # NCHW
    dshape = [3, 32, 32]
    input = fluid.layers.data(name='data', shape=dshape, dtype='float32')
    label = fluid.layers.data(name='label', shape=[1], dtype='int64')

    # Train program
    predict = resnet_cifar10(input, class_dim)
    cost = fluid.layers.cross_entropy(input=predict, label=label)
    avg_cost = fluid.layers.mean(x=cost)

    # Evaluator
    #accuracy = fluid.evaluator.Evaluator(input=predict, label=label)
   
    batch_size_tensor = fluid.layers.create_tensor(dtype='int64')
    batch_acc = fluid.layers.accuracy(
        input=predict, label=label, total=batch_size_tensor)
    accuracy = fluid.average.WeightedAverage()

    # inference program
    inference_program = fluid.default_main_program().clone(for_test=True)

    # Optimization
    optimizer = fluid.optimizer.Momentum(learning_rate=0.01, momentum=0.9)
    opts = optimizer.minimize(avg_cost)
    fluid.memory_optimize(fluid.default_main_program())

    train_reader = paddle.batch(
        paddle.dataset.cifar.train10(), batch_size=batch_size)

    test_reader = paddle.batch(
        paddle.dataset.cifar.test10(), batch_size=batch_size)

    # Initialize executor
    place = fluid.CPUPlace() if args.device == 'CPU' else fluid.CUDAPlace(0)
    exe = fluid.Executor(place)

    # Parameter initialization
    exe.run(fluid.default_startup_program())

    def test(exe):
        test_accuracy = fluid.average.WeightedAverage()
        for batch_id, data in enumerate(test_reader()):
            img_data = np.array(map(lambda x: x[0].reshape(dshape),
                                    data)).astype("float32")
            y_data = np.array(map(lambda x: x[1], data)).astype("int64")
            y_data = y_data.reshape([-1, 1])

            acc, weight = exe.run(inference_program,
                                  feed={"data": img_data,
                                        "label": y_data},
                                  fetch_list=[batch_acc, batch_size_tensor])
            test_accuracy.add(value=acc, weight=weight)

        return test_accuracy.eval()

    im_num = 0
    total_train_time = 0.0
    for pass_id in range(args.pass_num):
        iter = 0
        every_pass_loss = []
        accuracy.reset()
        pass_duration = 0.0
        for batch_id, data in enumerate(train_reader()):
            logger.warning('Batch {}'.format(batch_id))
            batch_start = time.time()
            if iter == iterations:
                break
            image = np.array(map(lambda x: x[0].reshape(dshape), data)).astype(
                'float32')
            label = np.array(map(lambda x: x[1], data)).astype('int64')
            label = label.reshape([-1, 1])

            loss, acc, weight = exe.run(
                fluid.default_main_program(),
                feed={'data': image,
                      'label': label},
                fetch_list=[avg_cost, batch_acc, batch_size_tensor])

            batch_end = time.time()
            every_pass_loss.append(loss)
            accuracy.add(value=acc, weight=weight)
        

            if iter >= args.skip_batch_num or pass_id != 0:
                batch_duration = time.time() - batch_start
                pass_duration += batch_duration
                im_num += label.shape[0]

            iter += 1

            print(
                    "Pass = %d, Iter = %d, Loss = %f, Accuracy = %f" %
                    (pass_id, iter, loss, acc))
        pass_train_acc = accuracy.eval()
        pass_test_acc = test(exe)

        total_train_time += pass_duration
        pass_train_loss = np.mean(every_pass_loss) 
        print(
            "Pass:%d, Loss:%f, Train Accuray:%f, Test Accuray:%f, Handle Images Duration: %f\n"
            % (pass_id, pass_train_loss, pass_train_acc,
               pass_test_acc, pass_duration))
    if pass_id == args.pass_num - 1:
        train_cost_kpi.add_record(np.array(pass_train_loss, dtype='float32'))
        train_cost_kpi.persist()
        train_acc_kpi.add_record(np.array(pass_train_acc, dtype='float32'))
        train_acc_kpi.persist()
        test_acc_kpi.add_record(np.array(pass_test_acc, dtype='float32'))
        test_acc_kpi.persist()
        train_duration_kpi.add_record(batch_end - batch_start)
        train_duration_kpi.persist()

    if total_train_time > 0.0:
        examples_per_sec = im_num / total_train_time
        sec_per_batch = total_train_time / \
            (iter * args.pass_num - args.skip_batch_num)
        train_speed_kpi.add_record(np.array(examples_per_sec, dtype='float32'))
        train_speed_kpi.persist()


def parse_args():
    parser = argparse.ArgumentParser('model')
    parser.add_argument('--batch_size', type=int)
    parser.add_argument('--device', type=str, choices=('CPU', 'GPU'))
    parser.add_argument('--iters', type=int)
    parser.add_argument(
        '--pass_num', type=int, default=3, help='The number of passes.')
    parser.add_argument(
        '--skip_batch_num',
        type=int,
        default=5,
        help='The first num of minibatch num to skip, for better performance test'
    )
    args = parser.parse_args()
    return args


args = parse_args()
train(args.batch_size, args.device, 1, args.iters)

for kpi in tracking_kpis:
    kpi.persist()
