import unittest

class TestSum(unittest.TestCase):

    def test_sum(self):
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")

    def test_sum_tuple(self):
        self.assertEqual(sum((1, 2, 2)), 6, "Should be 6")

class TestSum2(unittest.TestCase):
    def test_sum3(self):
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")


if __name__ == '__main__':
    unittest.main()


    def standarizeFile(self):
        if self.fold_increased:
            raise Exception("already fold increased")
        else:
            self.standarized = True
            m = max(self.point_list)
            print("max", m)
            self.point_list = [round(point * 100 / m, 2) for point in self.point_list]
            plt.plot(self.point_list)
            plt.show()
            return self.point_list