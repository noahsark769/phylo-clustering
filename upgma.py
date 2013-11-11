def read_matrix_to_upgma(filename):
	matrix = []
	with open(filename, 'r') as f:
		for line in f:
			matrix.append([int(i) for i in line.strip().split(" ")])
	labels = ["dog", "bear", "raccoon", "weasel", "seal", "sea lion", "cat", "monkey"]
	return cluster_from_matrix(matrix, labels)

def cluster_from_matrix(matrix, labels):
	return UPGMAFactory(matrix, labels).cluster();

def string_cluster(cluster):
	"""Print a cluster of the form: [<[<B>(0.5), <C>(0.5)]>(1.75), <[<A>(1.0), <D>(1.0)]>(1.25)>]"""
	s = ""
	if cluster.has_only_one():
		s += str(cluster.elem1)
	else:
		s += "[<" + string_cluster(cluster.elem1) + ">(" + str(cluster.height - cluster.elem1.height) + ")," +\
		" <" + string_cluster(cluster.elem2) + ">(" + str(cluster.height - cluster.elem2.height) + ")]"
	return s

class UPGMAFactory(object):
	def __init__(self, matrix, labels):
		self.labels = labels
		self.diss_map = {}
		for i, row in enumerate(matrix):
			for j, score in enumerate(row):
				self.diss_map[(self.labels[i], self.labels[j])] = score
		# dissimilarity map has been initialized

	def cluster(self):
		clusters = [UPGMACluster(self.diss_map, label) for label in self.labels]
		while len(clusters) != 2:
			min_cluster1 = None
			min_cluster2 = None
			min_distance = float("inf")
			for cluster1 in clusters:
				for cluster2 in clusters:
					if cluster1 == cluster2:
						continue
					distance = cluster1.distance_to_cluster(cluster2)
					if min_cluster1 is None or min_cluster2 is None or distance < min_distance:
						min_distance = distance
						min_cluster1 = cluster1
						min_cluster2 = cluster2
			new_cluster = UPGMACluster.create_from_clusters(self.diss_map, min_cluster1, min_cluster2)
			clusters.remove(min_cluster1)
			clusters.remove(min_cluster2)
			clusters.append(new_cluster)
		return UPGMACluster.create_from_clusters(self.diss_map, clusters[0], clusters[1])

class UPGMACluster(object):
	def __init__(self, diss_map, elem1, elem2=None, height=0.0):
		self.elem1 = elem1
		self.elem2 = elem2
		self.diss_map = diss_map
		self.height = height
		if elem2 is not None:
			self.length = 2
		else:
			self.length = 1

	@classmethod
	def create_from_clusters(cls, diss_map, cluster1, cluster2):
		new_cluster = cls(diss_map, cluster1, cluster2, float(cluster1.distance_to_cluster(cluster2) / 2))
		new_cluster.length = cluster1.length + cluster2.length
		return new_cluster

	def __str__(self):
		return "<[\n  " + str(self.elem1) + ",\n  " + str(self.elem2) + "\n]>"

	def __eq__(self, other_cluster):
		return str(self) == str(other_cluster)

	def has_only_one(self):
		"""If this is true, then elem2 is none and elem1 is a basestring."""
		return self.length == 1

	def distance_to_cluster(self, other_cluster):
		# if calculating the distance between two single points, use the dissimilarity map
		if self.has_only_one() and other_cluster.has_only_one():
			return float(self.diss_map[(self.elem1, other_cluster.elem1)])
		elif not self.has_only_one() and other_cluster.has_only_one():
			# d_il|C_i| + d_jl|C_j|
			numerator = self.elem1.distance_to_cluster(other_cluster) * self.elem1.length + self.elem2.distance_to_cluster(other_cluster) * self.elem2.length
			denominator = self.elem1.length + self.elem2.length
			return float(numerator / denominator)
		elif self.has_only_one() and not other_cluster.has_only_one():
			# d_il|C_i| + d_jl|C_j|
			numerator = other_cluster.elem1.distance_to_cluster(self) * other_cluster.elem1.length + other_cluster.elem2.distance_to_cluster(self) * other_cluster.elem2.length
			denominator = other_cluster.elem1.length + other_cluster.elem2.length
			return float(numerator / denominator)
		else:
			# two clusters, each of more than one
			numerator = 0
			for subcluster in [self.elem1, self.elem2]:
				for other_subcluster in [other_cluster.elem1, other_cluster.elem2]:
					numerator += subcluster.distance_to_cluster(other_subcluster)
			denominator = self.length * other_cluster.length
			return float(numerator / denominator)
