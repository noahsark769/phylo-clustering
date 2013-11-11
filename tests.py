import unittest

from upgma import cluster_from_matrix
from upgma import string_cluster

class UPGMATestCase(unittest.TestCase):

	def test_regular_cases(self):
		self.assertEqual(
			"[<[<B>(0.5), <C>(0.5)]>(1.75), <[<A>(1.0), <D>(1.0)]>(1.25)]",
			string_cluster(
				cluster_from_matrix([
					[0, 6, 4, 2],
					[6, 0, 1, 3],
					[4, 1, 0, 5],
					[2, 3, 5, 0]
				],
				['A', 'B', 'C', 'D']
				)
			)
		)

if __name__ == '__main__':
	unittest.main()