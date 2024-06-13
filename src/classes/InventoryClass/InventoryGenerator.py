import os
import re
import json
from datetime import datetime

def get_inventory_folder():
    """
    Get the folder name for storing the generated inventory JSON files.

    Returns:
    str: The folder name.
    """
    folder_name = "public/GeneratedInventories"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def find_file(filename):
    """
    Search for the specified file in the current directory, one level up, and one level down.

    Args:
    filename (str): The name of the file to search for.

    Returns:
    str: The path to the found file, or None if the file is not found.
    """
    # Check in the current directory
    if os.path.isfile(filename):
        return os.path.abspath(filename)
    
    # Check in the parent directory
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
    parent_path = os.path.join(parent_dir, filename)
    if os.path.isfile(parent_path):
        return parent_path
    
    # Check in subdirectories (one level down)
    for root, dirs, files in os.walk(os.getcwd()):
        if filename in files:
            return os.path.join(root, filename)

    return None

def parse_publications(file_path):
    """
    Parse the content of the given text file containing publication information
    and organize it into a structured dictionary.

    Args:
    file_path (str): The path to the text file containing publication information.

    Returns:
    list: A list of dictionaries, each representing a publication.
    list: A list of orphaned records that could not be parsed correctly.
    """
    file_path = find_file(file_path)
    if not file_path:
        print(f"File '{file_path}' not found.")
        return [], []

    with open(file_path, 'r') as file:
        content = file.read()

    publications = []
    orphaned_records = []
    language = None
    category = None
    name, jwId, edition = None, None, "Standard"

    for line in content.split('\n'):
        line = line.strip()
        if line.startswith("Language:"):
            language = line.split("Language:")[1].strip()
        elif line.startswith("Category:"):
            category = line.split("Category:")[1].strip()
        elif line.startswith("Name:"):
            name_line = line.split("Name:")[1].strip().replace('"', '')
            name_match = re.match(r'\(([^)]+)\)\s*(.+)', name_line)
            if name_match:
                jwId = name_match.group(1)
                name = name_match.group(2).strip()
            else:
                jwId = None
                name = name_line

            edition = "Standard"  # Default edition

            # Create and add the publication object
            if name and category and language:
                publication = {
                    "language": language,
                    "category": category,
                    "name": name,
                    "jwId": jwId,
                    "edition": edition,
                    "quantity": 0  # Set default quantity to 0
                }
                publications.append(publication)
            else:
                orphaned_records.append({
                    "language": language,
                    "category": category,
                    "name": name,
                    "jwId": jwId,
                    "edition": edition,
                    "quantity": 0  # Set default quantity to 0
                })
            name, jwId, edition = None, None, "Standard"  # Reset for next entry
        elif line.startswith("Edition:"):
            edition = line.split("Edition:")[1].strip()
            if publications:
                publications[-1]["edition"] = edition  # Update the edition of the last publication added

    return publications, orphaned_records


def save_orphaned_records(orphaned_records, folder):
    """
    Save the orphaned records to a JSON file in the specified folder.

    Args:
    orphaned_records (list): A list of orphaned records.
    folder (str): The folder to save the orphaned records file in.
    """
    if orphaned_records:
        orphaned_file = os.path.join(folder, "OrphanedRecords_" + datetime.now().strftime("%Y-%m-%d") + ".json")
        with open(orphaned_file, 'w') as file:
            json.dump(orphaned_records, file, indent=4)
        print(f"Orphaned records saved to: {orphaned_file} 😿😿😿😿")
    else:
        print("No orphaned records to save. 😸😸😸😸")

def edit_publication(publications):
    """
    Edit a publication by selecting it from the list of publications and
    modifying its attributes.

    Args:
    publications (list): A list containing parsed publication information.

    Returns:
    list: The updated list of publications.
    """
    print("Select a publication to edit:")
    for i, pub in enumerate(publications):
        print(f"{i+1}. {pub['name']} ({pub['jwId']}) - {pub['language']} - {pub['category']} - {pub['edition']} - {pub['quantity']}")
    pub_choice = input("Publication number: ")
    try:
        index = int(pub_choice) - 1
        publication = publications[index]
        print("Editing publication:")
        print(f"Name: {publication['name']}")
        print(f"jwId: {publication['jwId']}")
        print(f"Language: {publication['language']}")
        print(f"Category: {publication['category']}")
        print(f"Edition: {publication['edition']}")
        new_name = input("Enter new publication name (or press Enter to keep the same): ").strip()
        if new_name:
            publication["name"] = new_name
        new_jwId = input("Enter new jwId (or press Enter to keep the same): ").strip()
        if new_jwId:
            publication["jwId"] = new_jwId
        new_language = input("Enter new language (or press Enter to keep the same): ").strip()
        if new_language:
            publication["language"] = new_language
        new_category = input("Enter new category (or press Enter to keep the same): ").strip()
        if new_category:
            publication["category"] = new_category
        new_edition = input("Enter new edition (or press Enter to keep the same): ").strip()
        if new_edition:
            publication["edition"] = new_edition
        new_quantity = input("Enter new quantity (or press Enter to keep the same): ").strip()
        if new_quantity:
            publication["quantity"] = int(new_quantity)
        print("Publication edited successfully!")
        return publications
    except (ValueError, IndexError):
        print("Invalid selection!")
        return publications

def add_publication(publications):
    """
    Add a new publication to the list of publications.

    Args:
    publications (list): A list containing parsed publication information.

    Returns:
    list: The updated list of publications.
    """
    print("Adding a new publication:")
    publication = {}
    publication["name"] = input("Enter publication name: ").strip()
    publication["jwId"] = input("Enter jwId: ").strip()
    publication["quantity"] = 0  # Set default quantity to 0
    publication["language"] = input("Enter language: ").strip()
    publication["category"] = input("Enter category: ").strip()
    publication["edition"] = input("Enter edition (or press Enter to use 'Standard'): ").strip() or "Standard"
    publications.append(publication)
    print("Publication added successfully!")
    return publications

def main():
    """
    Main function to parse the input file containing publication information,
    generate a structured list, and save it to a JSON file.
    """
    try:
        while True:
            print("\nOptions:")
            print("1. Edit publication 🖊 ")
            print("2. Add publication 📚")
            print("3. Generate JSON document 📄")
            print("4. Exit 🖐")
            choice = input("Enter your choice: ")
            if choice == "1":
                publications, orphaned_records = parse_publications("PublicationsList.txt")
                publications = edit_publication(publications)
            elif choice == "2":
                publications, orphaned_records = parse_publications("PublicationsList.txt")
                publications = add_publication(publications)
            elif choice == "3":
                input_file = "PublicationsList.txt"
                output_folder = get_inventory_folder()
                publications, orphaned_records = parse_publications(input_file)
                output_file = os.path.join(output_folder, "Inventory_" + datetime.now().strftime("%Y-%m-%d") + ".json")
                with open(output_file, 'w') as file:
                    json.dump(publications, file, indent=4)
                print(f"\nJSON document generated successfully! ✅\n📁 File has been saved to 🎯: {output_file} 📁")
                save_orphaned_records(orphaned_records, output_folder)
                print('----------------------\n📚📚📚📚📚📚📚📚')
            elif choice == "4":
                print("Exiting...Good Bye. 🌆🌆🌆🌆")
                break
            else:
                print("⛔ Invalid choice! Please enter a valid option. ⛔ (1-4)")
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
