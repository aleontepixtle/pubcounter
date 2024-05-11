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
    folder_name = "GeneratedInventories"
    index = 1
    while os.path.exists(folder_name):
        index += 1
        folder_name = f"GeneratedInventories_{index}"
    return folder_name

def parse_publications(file_path):
    """
    Parse the content of the given text file containing publication information
    and organize it into a structured dictionary.

    Args:
    file_path (str): The path to the text file containing publication information.

    Returns:
    dict: A dictionary containing parsed publication information organized by category.
    """
    with open(file_path, 'r') as file:
        content = file.read()

    publications = {}
    category = None
    sub_category = None
    edition = None
    orphaned_records = []

    for line in content.split('\n'):
        if line.startswith("Category:"):
            category = line.split("Category:")[1].strip()
            publications[category] = []
            sub_category = None
            edition = None
        elif line.startswith("Sub-Category:"):
            sub_category = line.split("Sub-Category:")[1].strip()
            edition = None
        elif line.startswith("Edition:"):
            edition = line.split("Edition:")[1].strip()

        elif line.strip() != "":
            publication_match = re.match(r'\(([^)]+)\)\s*(.+)', line)  # Match publication name and jwId
            if publication_match:
                jwId = publication_match.group(1)
                publication_name = publication_match.group(2).strip('"').strip()  # Extract publication name and remove surrounding double quotes
            else:
                publication_name = line.strip('"').strip()  # If jwId is not found, consider the entire line as publication name
                jwId = None

            if jwId:
                if sub_category:
                    publication = {
                        "publicationName": publication_name,
                        "jwId": jwId,
                        "quantity": 0,  # Set default quantity to 0
                        "category": category,
                        "subCategory": sub_category
                    }
                    if edition:
                        publication["edition"] = edition
                else:
                    publication = {
                        "publicationName": publication_name,
                        "jwId": jwId,
                        "quantity": 0,  # Set default quantity to 0
                        "category": category
                    }
                    if edition:
                        publication["edition"] = edition

                publications[category].append(publication)
            else:
                orphaned_records.append({
                    "publicationName": publication_name,
                    "category": category,
                    "subCategory": sub_category if sub_category else None,
                    "edition": edition if edition else None
                })

    return publications, orphaned_records

def edit_publication(publications):
    """
    Edit a publication by selecting it from the list of publications and
    modifying its attributes.

    Args:
    publications (dict): A dictionary containing parsed publication information.

    Returns:
    dict: The updated dictionary of publications.
    """
    print("Select a publication to edit:")
    for category, pubs in publications.items():
        print(f"{category}:")
        for i, pub in enumerate(pubs):
            print(f"{i+1}. {pub['publicationName']} ({pub['jwId']})")
    print("Enter the number of the publication to edit:")
    category_choice = input("Category: ")
    try:
        category_choice = int(category_choice)
        index = category_choice - 1
        category = list(publications.keys())[index]
        pubs = publications[category]
        print(f"Publications in {category}:")
        for i, pub in enumerate(pubs):
            print(f"{i+1}. {pub['publicationName']} ({pub['jwId']})")
        pub_choice = input("Publication number: ")
        try:
            pub_choice = int(pub_choice)
            index = pub_choice - 1
            publication = pubs[index]
            print("Editing publication:")
            print(f"Publication Name: {publication['publicationName']}")
            print(f"jwId: {publication['jwId']}")
            print(f"Category: {publication['category']}")
            print(f"Sub-Category: {publication['subCategory'] if 'subCategory' in publication else None}")
            print(f"Edition: {publication['edition'] if 'edition' in publication else None}")
            new_name = input("Enter new publication name (or press Enter to keep the same): ").strip()
            if new_name:
                publication["publicationName"] = new_name
            new_jwId = input("Enter new jwId (or press Enter to keep the same): ").strip()
            if new_jwId:
                publication["jwId"] = new_jwId
            new_category = input("Enter new category (or press Enter to keep the same): ").strip()
            if new_category:
                publication["category"] = new_category
            new_sub_category = input("Enter new sub-category (or press Enter to keep the same): ").strip()
            if new_sub_category:
                publication["subCategory"] = new_sub_category
            new_edition = input("Enter new edition (or press Enter to keep the same): ").strip()
            if new_edition:
                publication["edition"] = new_edition
            print("Publication edited successfully!")
            return publications
        except (ValueError, IndexError):
            print("Invalid publication number!")
            return publications
    except (ValueError, IndexError):
        print("Invalid category number!")
        return publications

def add_publication(publications):
    """
    Add a new publication to the list of publications.

    Args:
    publications (dict): A dictionary containing parsed publication information.

    Returns:
    dict: The updated dictionary of publications.
    """
    print("Adding a new publication:")
    publication = {}
    publication["publicationName"] = input("Enter publication name: ").strip()
    publication["jwId"] = input("Enter jwId: ").strip()
    publication["quantity"] = 0  # Set default quantity to 0
    publication["category"] = input("Enter category: ").strip()
    publication["subCategory"] = input("Enter sub-category (or press Enter to skip): ").strip()
    publication["edition"] = input("Enter edition (or press Enter to skip): ").strip()
    category = publication["category"]
    if category not in publications:
        publications[category] = []
    publications[category].append(publication)
    print("Publication added successfully!")
    return publications

def main():
    """
    Main function to parse the input file containing publication information,
    generate a structured dictionary, and save it to a JSON file.
    """
    try:
        while True:
            print("\nOptions:")
            print("1. Edit publication")
            print("2. Add publication")
            print("3. Generate JSON document")
            print("4. Exit")
            choice = input("Enter your choice: ")
            if choice == "1":
                publications, _ = parse_publications("PublicationsList.txt")
                publications = edit_publication(publications)
            elif choice == "2":
                publications, _ = parse_publications("PublicationsList.txt")
                publications = add_publication(publications)
            elif choice == "3":
                input_file = "PublicationsList.txt"
                output_folder = get_inventory_folder()
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)  # Create the directory if it doesn't exist
                output_file = os.path.join(output_folder, "Inventory_" + datetime.now().strftime("%Y-%m-%d") + ".json")
                orphaned_records_file = os.path.join(output_folder, "Orphaned_Records_" + datetime.now().strftime("%Y-%m-%d") + ".json")
                publications, orphaned_records = parse_publications(input_file)
                if orphaned_records:
                    with open(orphaned_records_file, 'w') as orphaned_file:
                        json.dump(orphaned_records, orphaned_file, indent=4)
                with open(output_file, 'w') as file:
                    json.dump(publications, file, indent=4)
                print(f"JSON document generated successfully: {output_file}")
            elif choice == "4":
                print("Exiting...")
                break
            else:
                print("Invalid choice! Please enter a valid option.")
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
