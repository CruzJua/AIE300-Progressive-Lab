import torch

def header(title):
    print("\033[36m", "=" * 50, "\033[0m")
    print("\033[36m", title, "\033[0m")
    print("\033[36m", "=" * 50, "\033[0m")

def footer():
    print("\033[31m", "=" * 50, "\033[0m")


header("Part 1: PyTorch Fundamentals")

from_list = torch.tensor([[1.0, 2.0, 3.0],
                           [4.0, 5.0, 6.0],
                           [7.0, 8.0, 9.0]])
print(f"From list:\n{from_list}\n")

random_tensor = torch.randn(3, 3)
print(f"torch.randn(3, 3):\n{random_tensor}\n")

print(f"Matrix Multiplication:\n{torch.matmul(random_tensor, from_list)}\n")
print(f"Matrix Addition: \n{torch.add(random_tensor, from_list)}\n")

x = torch.tensor(3.0, requires_grad=True)
y = x ** 2 + 2 * x + 1    # y = x^2 + 2x + 1
y.backward()                # dy/dx = 2x + 2
print(f"x = {x.item()}, dy/dx = {x.grad.item()}")  # x = 3.0, dy/dx = 8.0

footer()

header("Part 2.1: Train a Model")

from sklearn.datasets import load_iris
import torch.nn as nn
from torch.utils.data import random_split, DataLoader, TensorDataset

class SimpleClassifier(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super().__init__()
        self.layer1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.layer2(x)
        return x

model = SimpleClassifier(input_size=4, hidden_size=16, num_classes=3)

data = load_iris()
X = torch.tensor(data.data, dtype=torch.float32)
y = torch.tensor(data.target, dtype=torch.long)
dataset = TensorDataset(X, y)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

train_size = int(0.8 * len(dataset))
test_size = len(dataset) - train_size

training_data, test_data = random_split(dataset, [train_size, test_size])

train_loader = DataLoader(training_data, batch_size=32, shuffle=True)
test_loader = DataLoader(test_data, batch_size=32, shuffle=False)

for epoch in range(50):
    model.train()
    for features, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(features)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}, Loss: {loss.item()}")
footer()

header("Part 2.2: Test Model")

model.eval()
with torch.no_grad():
    total = 0
    correct = 0
    for features, labels in test_loader:
        outputs = model(features)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
print(f"Accuracy: {100 * correct / total:.2f}%")

torch.save(model.state_dict(), "model.pth")
footer()
