import numpy as np
from scipy.optimize import line_search, minimize_scalar


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def compute_loss(w, X, y):
    z = X.dot(w)
    p = sigmoid(z)
    loss = -np.mean(y * np.log(p + 1e-15) + (1 - y) * np.log(1 - p + 1e-15))
    return loss


def compute_gradient(w, X, y):
    z = X.dot(w)
    p = sigmoid(z)
    gradient = X.T.dot(p - y) / len(y)
    return gradient


def compute_hessian(w, X, y):
    z = X.dot(w)
    p = sigmoid(z)
    D = np.diag(p * (1 - p))
    hessian = X.T.dot(D).dot(X) / len(y)
    return hessian


def gradient_descent(X, y, line_search_method, max_iter=1000, tol=1e-6):
    n_features = X.shape[1]
    w = np.zeros(n_features)

    for _ in range(max_iter):
        grad = compute_gradient(w, X, y)
        if np.linalg.norm(grad) < tol:
            break

        if line_search_method == 'armijo':
            alpha = armijo_line_search(w, grad, X, y)
        elif line_search_method == 'wolfe':
            alpha = wolfe_line_search(w, grad, X, y)
        elif line_search_method == 'lipschitz':
            alpha = lipschitz_line_search(w, X, y)
        elif line_search_method == 'golden-section-search':
            alpha = golden_section_line_search(w, grad, X, y)
        else:
            alpha = scalar_line_search(w, grad, X, y, method='brent')

        w = w - alpha * grad

    return w


def newton_raphson(X, y, line_search_method, max_iter=1000, tol=1e-6):
    n_features = X.shape[1]
    w = np.zeros(n_features)

    for _ in range(max_iter):
        grad = compute_gradient(w, X, y)
        hess = compute_hessian(w, X, y)
        # direction = np.linalg.solve(hess, grad)

        if np.linalg.norm(grad) < tol:
            break

        if line_search_method == 'armijo':
            alpha = armijo_line_search(w, grad, X, y)
        elif line_search_method == 'wolfe':
            alpha = wolfe_line_search(w, grad, X, y)
        elif line_search_method == 'lipschitz':
            alpha = lipschitz_line_search(w, X, y)
        elif line_search_method == 'golden-section-search':
            alpha = golden_section_line_search(w, grad, X, y)
        else:
            alpha = scalar_line_search(w, grad, X, y, method='brent')

        w = w - alpha * grad

    return w


def armijo_line_search(w, grad, X, y, alpha=1.0, beta=0.5, sigma=0.1):
    current_loss = compute_loss(w, X, y)
    grad = compute_gradient(w, X, y)

    while True:
        new_w = w - alpha * grad
        new_loss = compute_loss(new_w, X, y)
        expected_loss = current_loss - sigma * alpha * np.dot(grad, grad)

        if new_loss <= expected_loss:
            return alpha
        alpha *= beta


def wolfe_line_search(w, grad, X, y, alpha=1.0, beta=0.5, c1=1e-4, c2=0.9):
    current_loss = compute_loss(w, X, y)
    grad = compute_gradient(w, X, y)

    while True:
        new_w = w - alpha * grad
        new_loss = compute_loss(new_w, X, y)
        new_grad = compute_gradient(new_w, X, y)

        armijo_condition = new_loss <= current_loss - c1 * alpha * np.dot(grad, grad)
        curvature_condition = np.dot(new_grad, grad) >= c2 * np.dot(grad, grad)

        if armijo_condition and curvature_condition:
            return alpha
        alpha *= beta


def lipschitz_line_search(w, X, y, L=1.0):
    grad = compute_gradient(w, X, y)

    # Simple estimation - can be improved
    w_new = w - (1 / L) * grad
    grad_new = compute_gradient(w_new, X, y)

    while np.linalg.norm(grad_new - grad) > 0.1 * L * np.linalg.norm(w_new - w):
        L *= 2
        w_new = w - (1 / L) * grad
        grad_new = compute_gradient(w_new, X, y)

    return 1 / L


def scalar_line_search(w, grad, X, y, method='brent'):
    def f(alpha):
        return compute_loss(w - alpha * grad, X, y)

    res = minimize_scalar(f, method=method)
    return res.x


def golden_section_line_search(w, grad, X, y, tol=1e-6, max_iter=100):
    def f(alpha):
        new_w = w - alpha * grad
        return logistic_loss(new_w, X, y)

    a, b = 0, 1
    gr = (np.sqrt(5) + 1) / 2

    c = b - (b - a) / gr
    d = a + (b - a) / gr

    for _ in range(max_iter):
        if f(c) < f(d):
            b = d
        else:
            a = c

        c = b - (b - a) / gr
        d = a + (b - a) / gr

        if abs(b - a) < tol:
            break

    return (a + b) / 2


def solve(optimization_method_name, line_search_method_name, X, y):
    X = np.array(X, dtype=np.float64)
    y = np.array(y, dtype=np.float64)

    if optimization_method_name == 'gradient-descent':
        w = gradient_descent(X, y, line_search_method_name)
    elif optimization_method_name == 'newton-raphson':
        w = newton_raphson(X, y, line_search_method_name)
    else:
        raise ValueError(f"Unknown optimization method: {optimization_method_name}")

    return compute_loss(w, X, y)