const API_URL = "http://localhost:8000/items";

const itemContainer = document.getElementById("item-container");
const itemForm = document.getElementById("item-form");
const itemName = document.getElementById("item-name");
const itemDescription = document.getElementById("item-description");


itemForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const item = {
        name: itemName.value,
        description: itemDescription.value
    };

    try {
        const res = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(item)
        });
        if (!res.ok) throw new Error("Failed to create item");
        const created = await res.json();
        addItemCard(created);
        itemForm.reset();
    } catch (err) {
        console.error(err);
        alert("Error creating item");
    }
});

document.addEventListener("DOMContentLoaded", () => {
    renderItems();
});


async function renderItems() {
    itemContainer.innerHTML = "Loading...";
    try {
        const res = await fetch(API_URL);
        if (!res.ok) throw new Error("Failed to fetch items");
        const items = await res.json();

        itemContainer.innerHTML = "";
        if (items.length === 0) {
            itemContainer.innerHTML = "NO ITEMS FOUND";
        } else {
            items.forEach((item) => {
                addItemCard(item);
            });
        }
    } catch (err) {
        console.error(err);
        itemContainer.innerHTML = "ERROR LOADING ITEMS";
    }
}

function addItemCard(item) {
    if (itemContainer.textContent === "NO ITEMS FOUND") {
        itemContainer.innerHTML = "";
    }
    const itemCard = document.createElement("div");
    itemCard.classList.add("item-card");
    itemCard.dataset.id = item.id;
    itemCard.innerHTML = `
        <p>Item Name: ${item.name}</p>
        <p>Item Description: ${item.description || ""}</p>
        <div class="item-card-buttons">
            <button onclick="editItem('${item.id}')">Edit</button>
            <button onclick="deleteItem('${item.id}')">Delete</button>
        </div>
    `;
    itemContainer.appendChild(itemCard);
}

async function deleteItem(id) {
    try {
        const res = await fetch(`${API_URL}/${id}`, { method: "DELETE" });
        if (!res.ok) throw new Error("Failed to delete item");
        renderItems();
    } catch (err) {
        console.error(err);
        alert("Error deleting item");
    }
}

async function editItem(id) {
    const newName = prompt("New item name:");
    if (newName === null) return;
    const newDesc = prompt("New item description:");
    if (newDesc === null) return;

    try {
        const res = await fetch(`${API_URL}/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: newName, description: newDesc, id: id })
        });
        if (!res.ok) throw new Error("Failed to update item");
        renderItems();
    } catch (err) {
        console.error(err);
        alert("Error updating item");
    }
}
