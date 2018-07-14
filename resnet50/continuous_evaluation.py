import os
import sys
sys.path.append(os.environ['ceroot'])
from kpi import CostKpi, DurationKpi, AccKpi

cifar10_128_AllReduce_GPU_train_acc_kpi = AccKpi(
    'cifar10_128_AlReduce_GPU_train_acc', 0.03, 0, actived=True)
cifar10_128_AllReduce_GPU_train_speed_kpi = AccKpi(
    'cifar10_128_AllReduce_GPU_train_speed', 0.06, 0, actived=True)
cifar10_128_AllReduce_gpu_memory_kpi = DurationKpi(
    'cifar10_128_AllReduce_gpu_memory', 0.1, 0, actived=True)

cifar10_128_Reduce_GPU_train_acc_kpi = AccKpi(
    'cifar10_128_Reduce_GPU_train_acc', 0.03, 0, actived=True)
cifar10_128_Reduce_GPU_train_speed_kpi = AccKpi(
    'cifar10_128_Reduce_GPU_train_speed', 0.06, 0, actived=True)
cifar10_128_Reduce_gpu_memory_kpi = DurationKpi(
    'cifar10_128_Reduce_gpu_memory', 0.1, 0, actived=True)

cifar10_128_AllReduce_CPU_train_acc_kpi = AccKpi(
    'cifar10_128_AllReduce_CPU_train_acc', 0.03, 0, actived=True)
cifar10_128_AllReduce_CPU_train_speed_kpi = AccKpi(
    'cifar10_128_AllReduce_CPU_train_speed', 0.06, 0, actived=True)

cifar10_128_Reduce_CPU_train_acc_kpi = AccKpi(
    'cifar10_128_Reduce_CPU_train_acc', 0.03, 0, actived=True)
cifar10_128_Reduce_CPU_train_speed_kpi = AccKpi(
    'cifar10_128_Reduce_CPU_train_speed', 0.06, 0, actived=True)

flowers_64_AllReduce_GPU_train_acc_kpi = AccKpi(
    'flowers_64_AllReduce_GPU_train_acc', 0.03, 0, actived=True)
flowers_64_AllReduce_GPU_train_speed_kpi = AccKpi(
    'flowers_64_AllReduce_GPU_train_speed', 0.06, 0, actived=True)
flowers_64_AllReduce_gpu_memory_kpi = DurationKpi(
    'flowers_64_AllReduce_gpu_memory', 0.1, 0, actived=True)

flowers_64_Reduce_GPU_train_acc_kpi = AccKpi(
    'flowers_64_Reduce_GPU_train_acc', 0.03, 0, actived=True)
flowers_64_Reduce_GPU_train_speed_kpi = AccKpi(
    'flowers_64_Reduce_GPU_train_speed', 0.06, 0, actived=True)
flowers_64_Reduce_gpu_memory_kpi = DurationKpi(
    'flowers_64_Reduce_gpu_memory', 0.1, 0, actived=True)

flowers_64_AllReduce_CPU_train_acc_kpi = AccKpi(
    'flowers_64_AllReduce_CPU_train_acc', 0.03, 0, actived=True)
flowers_64_AllReduce_CPU_train_speed_kpi = AccKpi(
    'flowers_64_AllReduce_CPU_train_speed', 0.06, 0, actived=True)

flowers_64_Reduce_CPU_train_acc_kpi = AccKpi(
    'flowers_64_Reduce_CPU_train_acc', 0.03, 0, actived=True)
flowers_64_Reduce_CPU_train_speed_kpi = AccKpi(
    'flowers_64_Reduce_CPU_train_speed', 0.06, 0, actived=True)

tracking_kpis = [
    cifar10_128_AllReduce_GPU_train_acc_kpi,
    cifar10_128_AllReduce_GPU_train_speed_kpi,
    cifar10_128_AllReduce_gpu_memory_kpi,
    cifar10_128_Reduce_GPU_train_acc_kpi,
    cifar10_128_Reduce_GPU_train_speed_kpi,
    cifar10_128_Reduce_gpu_memory_kpi,
    cifar10_128_AllReduce_CPU_train_acc_kpi,
    cifar10_128_AllReduce_CPU_train_speed_kpi,
    cifar10_128_Reduce_CPU_train_acc_kpi,
    cifar10_128_Reduce_CPU_train_speed_kpi,
    flowers_64_AllReduce_GPU_train_acc_kpi,
    flowers_64_AllReduce_GPU_train_speed_kpi,
    flowers_64_AllReduce_gpu_memory_kpi,
    flowers_64_Reduce_GPU_train_acc_kpi,
    flowers_64_Reduce_GPU_train_speed_kpi,
    flowers_64_Reduce_gpu_memory_kpi,
    flowers_64_AllReduce_CPU_train_acc_kpi,
    flowers_64_AllReduce_CPU_train_speed_kpi,
    flowers_64_Reduce_CPU_train_acc_kpi,
    flowers_64_Reduce_CPU_train_speed_kpi,
]
