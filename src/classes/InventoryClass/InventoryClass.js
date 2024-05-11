import React from 'react';
  
  const InventoryClass = () =>  {
	return (
	  <div>
	  </div>
	);
  }
  
  export default InventoryClass;
  /**
 * Represents an inventory of publications organized by category.
 */
class Inventory {
    /**
     * Constructs a new Inventory object with the given data.
     * @param {Object} data - The inventory data organized by category.
     */
    constructor(data) {
        this.data = data;
    }

    /**
     * Get publications belonging to a specific category.
     * @param {string} category - The category of publications to retrieve.
     * @returns {Array} An array of publications in the specified category.
     */
    getPublicationsByCategory(category) {
        return this.data[category] || [];
    }

    /**
     * Get all categories in the inventory.
     * @returns {Array} An array of all categories present in the inventory.
     */
    getCategories() {
        return Object.keys(this.data);
    }

    /**
     * Get all publications in the inventory.
     * @returns {Array} An array containing all publications in the inventory.
     */
    getAllPublications() {
        let allPublications = [];
        for (const category in this.data) {
            allPublications = allPublications.concat(this.data[category]);
        }
        return allPublications;
    }
}

// Function to find the latest numbered folder
async function findLatestFolder() {
    let latestFolder = "GeneratedInventories";
    let index = 1;
    while (await fetch(`./${latestFolder}_${index}`, { method: "HEAD" }).then(response => response.ok).catch(() => false)) {
        index++;
        latestFolder = `GeneratedInventories_${index}`;
    }
    return latestFolder;
}

// Function to import inventory data
async function importInventoryData() {
    const latestFolder = await findLatestFolder();
    const inventoryFiles = await fetch(`./${latestFolder}`).then(response => response.json());
    const inventoryFileNames = Object.keys(inventoryFiles);
    const inventoryFileName = inventoryFileNames.find(fileName => fileName.startsWith("Inventory"));
    const inventoryData = await fetch(`./${latestFolder}/${inventoryFileName}`).then(response => response.json());
    return inventoryData;
}

// Import the inventory data and create an Inventory object
importInventoryData().then(data => {
    const inventory = new Inventory(data);

    console.log("Publications in 'Books' category:");
    console.log(inventory.getPublicationsByCategory('Books'));

    console.log("\nAll categories:");
    console.log(inventory.getCategories());

    console.log("\nAll publications:");
    console.log(inventory.getAllPublications());
});
