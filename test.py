#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import numpy
import six

import chainer
from chainer import cuda
from chainer import gradient_check
from chainer import testing
from chainer.testing import condition
import bicnn


@testing.parameterize(*testing.product({
    'dtype': [numpy.float16, numpy.float32, numpy.float64],
}))
class TestKMaxPooling2D(unittest.TestCase):

    def setUp(self):
        self.x = numpy.random.uniform(
            -1, 1, (2, 3, 4, 7)).astype(self.dtype)
        self.gy = numpy.random.uniform(
            -1, 1, (2, 3, 4, 3)).astype(self.dtype)
        self.check_backward_options = {'eps': 2.0 ** -8}

    def check_forward(self, x_data):
        x = chainer.Variable(x_data)
        y = bicnn.k_max_pooling_2d(x, 3)
        self.assertEqual(y.data.dtype, self.dtype)
        y_data = cuda.to_cpu(y.data)

        self.assertEqual(self.gy.shape, y_data.shape)
        for k in six.moves.range(2):
            for c in six.moves.range(3):
                x = self.x[k, c]
                indexes = numpy.sort(numpy.argsort(-x)[:, :3])
                indexes += numpy.arange(4).reshape((4, 1)) * 7
                expect = numpy.take(x, indexes)
                testing.assert_allclose(expect, y_data[k, c])

    @condition.retry(3)
    def test_forward_cpu(self):
        self.check_forward(self.x)

    def check_backward(self, x_data, y_grad):
        gradient_check.check_backward(
            bicnn.KMaxPooling2D(k=3),
            x_data, y_grad, **self.check_backward_options)

    @condition.retry(3)
    def test_backward_cpu(self):
        self.check_backward(self.x, self.gy)


testing.run_module(__name__, __file__)
