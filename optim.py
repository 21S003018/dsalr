from const import EPSILON
from torch.optim.optimizer import Optimizer
from torch.nn import Linear
import torch

OBSERVW = -3


class Dsa(Optimizer):
    def __init__(self, params, lr_init=-7, meta_lr=0.6) -> None:
        self.params = list(params)
        self.meta_lr = meta_lr
        self.last_w_grad = []
        self.tmp_w_grad = None
        self.lr_matrix = []
        self.lr_grad = None
        for param in self.params:
            self.last_w_grad.append(torch.zeros(
                param.size(), device=param.device))
            self.lr_matrix.append(torch.ones(
                param.size(), device=param.device) * lr_init)
        super(Dsa, self).__init__(
            self.params, defaults=dict(lr=lr_init, meta_lr=meta_lr))
        pass

    def lr_autograd(self):
        self.lr_grad = []
        self.tmp_w_grad = []
        for param in self.params:
            if param.grad != None:
                self.tmp_w_grad.append(param.grad.clone())
            else:
                self.tmp_w_grad.append(torch.zeros(
                    param.size(), device=param.device))
        for i in range(len(self.last_w_grad)):
            grad = -torch.mul(self.last_w_grad[i], self.tmp_w_grad[i])
            grad = torch.mul(grad, 1/(grad.abs() + EPSILON))
            self.lr_grad.append(grad)
        self.last_w_grad = self.tmp_w_grad
        # print(self.last_w_grad[OBSERVW][0])
        print("param", self.params[OBSERVW][0][0])
        return

    def step(self, closure=None):
        self.lr_autograd()
        # print("alpha grad", self.lr_grad[OBSERVW][0][0])
        for i in range(len(self.lr_matrix)):
            self.lr_matrix[i] = self.lr_matrix[i] - \
                self.meta_lr * self.lr_grad[i]
        # print("alpha", self.lr_matrix[OBSERVW][0][0])
        # print("lr", torch.pow(2, self.lr_matrix[OBSERVW])[0][0])
        for i, param in enumerate(self.params):
            param.data -= torch.mul(param.grad *
                                    (1/(param.grad.abs() + EPSILON)), torch.pow(2, self.lr_matrix[i]))
        return