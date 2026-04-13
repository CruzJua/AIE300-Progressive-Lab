let items = [];

const itemContainer = document.getElementById("item-container");
const itemForm = document.getElementById("item-form");
const itemName = document.getElementById("item-name");
const itemDescription = document.getElementById("item-description");

itemForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const item = {
        name: itemName.value,
        description: itemDescription.value
    };
    items.push(item);
    renderItems();
    itemForm.reset();
});

function renderItems() {
    itemContainer.innerHTML = "";
    items.forEach((item) => {
        const itemCard = document.createElement("div");
        itemCard.classList.add("item-card");
        itemCard.innerHTML = `
            <p>Item Name: ${item.name}</p>
            <p>Item Description: ${item.description}</p>
            <div class="item-card-buttons">
                <button>Edit</button>
                <button>Delete</button>
            </div>
        `;
        itemContainer.appendChild(itemCard);
    });
}