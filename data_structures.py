class Slice():
    def __init__(self, kernel_name, start_time, end_time, subband_id, shape):
        self.kernel_name = kernel_name
        self.subband_id = subband_id
        self.slice = (start_time, end_time)
        self.shape = (shape[0], shape[1])

    def __str__(self):
        return f"Slice: kernel name: {self.kernel_name}, subband id: {self.subband_id}, slice: {self.slice}, shape: {self.shape}"
    
    def __repr__(self):
        return self.__str__()

class Timing_Data():
    def __init__(self):

        self.data = {}

    def add_new_data(self, kernel_name, slice):
        if kernel_name in self.data:
            self.data[kernel_name].append(slice)
        else:
            self.data[kernel_name] = [slice]

    def __str__(self):
        out_stream = []
        for key, value in self.data.items():
            out_stream.append(key + "\n")
            for item in value:
                out_stream.append("[" + item.__str__() + str("]\t"))
        return ''.join(out_stream)
    
    def __len__(self):
        length = 0
        for key, value in self.data.items():
            length += len(value)
        return length
    
    def kernelwise_len(self):
        for key, value in self.data.items():
            print(key, ":", len(value))

class Cluster():
    def __init__(self, id, kernels=None, slices=None, IMEM_layer=None, seed_kernel=None):
        self.id = id
        
        if kernels is not None:
            self.kernels = kernels
        else:
            self.kernels = []

        if slices is not None:
            self.slices = slices
        else:
            self.slices = []

        if IMEM_layer is not None:
            self.IMEM_layer = IMEM_layer
        else:
            self.IMEM_layer = -1
        
        if seed_kernel is not None:
            self.seed_kernel = seed_kernel
        else:
            self.seed_kernel = None

    def extend_cluster(self, kernels, slices):
        self.kernels.extend(kernels)
        self.slices.extend(slices)

    def extend_kernels(self, kernels):
        self.kernels.extend(kernels)

    def __str__(self):
        return f"Cluster: id: {self.id}, kernels: {self.kernels}, slices: {len(self.slices)}, IMEM layer: {self.IMEM_layer}"

    def __repr__(self):
        return self.__str__()

class Cluster_list():
    def __init__(self):
        self.clusters = {}