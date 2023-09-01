import os
import requests
import mysql, mysql.connector
from dotenv import load_dotenv
# project_folder = **** [This has been commented out for security reasons]
# load_dotenv('*****') [This has been commented out for security reasons]


def updateAnimalDatabase():
    """
    Fetches animals from the Shelterluv API and updates any details in the database that have changed.
    """

    def getAllAnimalsFromShelterluv(limit, offset):
        #api_key = os.getenv(***) [This has been commented out for security reasons]
        #response = requests.get('****' + str(limit) + '&offset=' + str(offset), headers={'***': api_key}).json() [This has been commented out for security reasons]
        return response

    def get_db_connection():
      cnx = mysql.connector.connect(
      #host="***",[This has been commented out for security reasons]
      #user="***",[This has been commented out for security reasons]
      #password=***,[This has been commented out for security reasons]
      #database="****")[This has been commented out for security reasons]
      return cnx

    i = 0
    response = getAllAnimalsFromShelterluv(100, i)
    animals = response['animals']
    while response['has_more']:
        i += 1
        response = getAllAnimalsFromShelterluv(100, 100*i)
        animals += response['animals']

    # submit animal to db
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM animal;")
    dbs = cursor.fetchall()
    dba = []
    for a in dbs:
        dba.append(a['id'])

    for animal in animals:
        if len(animal['Microchips']) > 0:
            microchip = 1
        else:
            microchip = 0
        if animal['Internal-ID'] in dba and animal['Type'] == "Cat":
            try:
                cursor.execute('UPDATE animal SET name = %s, type = %s, sex = %s, status = %s, in_foster = %s, current_weight = %s, size = %s, altered = %s, age = %s, breed = %s, color = %s, pattern = %s, description = %s, coverphoto = %s, microchip = %s WHERE id = %s;',
                (animal['Name'], animal['Type'], animal['Sex'], animal['Status'], animal['InFoster'], animal['CurrentWeightPounds'], animal['Size'], animal['Altered'], animal['Age'], animal['Breed'], animal['Color'], animal['Pattern'], animal['Description'], animal['CoverPhoto'], microchip, animal['Internal-ID']))
            except:
                cursor.execute('UPDATE animal SET name = %s, type = %s, sex = %s, status = %s, in_foster = %s, current_weight = %s, size = %s, altered = %s, age = %s, breed = %s, color = %s, description = %s, coverphoto = %s, microchip = %s WHERE id = %s;',
                (animal['Name'], animal['Type'], animal['Sex'], animal['Status'], animal['InFoster'], animal['CurrentWeightPounds'], animal['Size'], animal['Altered'], animal['Age'], animal['Breed'], animal['Color'], animal['Description'], animal['CoverPhoto'], microchip, animal['Internal-ID']))
            try:
                cursor.execute("UPDATE fees SET name = %s, price = %s, discount = %s, tax = %s WHERE id = %s;", (animal['AdoptionFeeGroup']['Name'], animal['AdoptionFeeGroup']['Price'], animal['AdoptionFeeGroup']['Discount'], animal['AdoptionFeeGroup']['Tax'], animal['Internal-ID']))
            except:
                print("No fees found.")
            try:
                cursor.execute("DELETE FROM attributes WHERE animal_id = %s", ([animal['Internal-ID']]))
                for attr in animal['Attributes']:
                    cursor.execute("INSERT INTO attributes (animal_id, attribute_id, attribute_name, publish) VALUES (%s, %s, %s, %s);", (animal['Internal-ID'], attr['Internal-ID'], attr['AttributeName'], attr['Publish']))
            except:
                print("No attributes found.")
            try:
                cursor.execute("DELETE FROM photos WHERE animal_id = %s", ([animal['Internal-ID']]))
                for photo in animal['Photos']:
                    cursor.execute("INSERT INTO photos (animal_id, url) VALUES (%s, %s);", (animal['Internal-ID'], photo))
            except:
                print("No photos found.")
            try:
                cursor.execute("DELETE FROM videos WHERE animal_id = %s", ([animal['Internal-ID']]))
                for video in animal['Videos']:
                    cursor.execute("INSERT INTO videos (animal_id, url) VALUES (%s, %s, %s);", (animal['Internal-ID'], video['EmbedUrl']))
            except:
                print("No videos found.")
            dba.remove(animal['Internal-ID'])
        elif animal['Internal-ID'] in dba and animal['Type'] == "Dog":
            cursor.execute('UPDATE animal SET name = %s, type = %s, sex = %s, status = %s, in_foster = %s, current_weight = %s, size = %s, altered = %s, age = %s, breed = %s, color = %s, description = %s, coverphoto = %s, microchip = %s WHERE id = %s;',
            (animal['Name'], animal['Type'], animal['Sex'], animal['Status'], animal['InFoster'], animal['CurrentWeightPounds'], animal['Size'], animal['Altered'], animal['Age'], animal['Breed'], animal['Color'], animal['Description'], animal['CoverPhoto'], microchip, animal['Internal-ID']))
            try:
                cursor.execute("UPDATE fees SET name = %s, price = %s, discount = %s, tax = %s WHERE id = %s;", (animal['AdoptionFeeGroup']['Name'], animal['AdoptionFeeGroup']['Price'], animal['AdoptionFeeGroup']['Discount'], animal['AdoptionFeeGroup']['Tax'], animal['Internal-ID']))
            except:
                print("No fees found.")
            try:
                cursor.execute("DELETE FROM attributes WHERE animal_id = %s", ([animal['Internal-ID']]))
                for attr in animal['Attributes']:
                    cursor.execute("INSERT INTO attributes (animal_id, attribute_id, attribute_name, publish) VALUES (%s, %s, %s, %s);", (animal['Internal-ID'], attr['Internal-ID'], attr['AttributeName'], attr['Publish']))
            except:
                print("No attributes found.")
            try:
                for photo in animal['Photos']:
                    cursor.execute("DELETE FROM photos WHERE animal_id = %s", ([animal['Internal-ID']]))
                    for photo in animal['Photos']:
                        cursor.execute("INSERT INTO photos (animal_id, url) VALUES (%s, %s);", (animal['Internal-ID'], photo))
            except:
                print("No photos found.")
            try:
                cursor.execute("DELETE FROM videos WHERE animal_id = %s", ([animal['Internal-ID']]))
                for video in animal['Videos']:
                    cursor.execute("INSERT INTO videos (animal_id, url) VALUES (%s, %s, %s);", (animal['Internal-ID'], video['EmbedUrl']))
            except:
                print("No videos found.")
            dba.remove(animal['Internal-ID'])
        else: ## not in dba
            try:
                cursor.execute("INSERT INTO animal (id, spr_id, name, type, sex, status, in_foster, current_weight, size, altered, age, breed, color, pattern, description, coverphoto, microchip) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                (animal['Internal-ID'], animal['ID'], animal['Name'], animal['Type'], animal['Sex'], animal['Status'], animal['InFoster'], animal['CurrentWeightPounds'], animal['Size'], animal['Altered'], animal['Age'], animal['Breed'], animal['Color'], animal['Pattern'], animal['Description'], animal['CoverPhoto'], microchip))
            except:
                cursor.execute("INSERT INTO animal (id, spr_id, name, type, sex, status, in_foster, current_weight, size, altered, age, breed, color, description, coverphoto, microchip) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                (animal['Internal-ID'], animal['ID'], animal['Name'], animal['Type'], animal['Sex'], animal['Status'], animal['InFoster'], animal['CurrentWeightPounds'], animal['Size'], animal['Altered'], animal['Age'], animal['Breed'], animal['Color'], animal['Description'], animal['CoverPhoto'], microchip))
            try:
                cursor.execute("INSERT INTO fees (id, name, price, discount, tax) VALUES (%s, %s, %s, %s, %s);", (animal['Internal-ID'], animal['AdoptionFeeGroup']['Name'], animal['AdoptionFeeGroup']['Price'], animal['AdoptionFeeGroup']['Discount'], animal['AdoptionFeeGroup']['Tax']))
            except:
                print("No fees found.")
            try:
                for attr in animal['Attributes']:
                    cursor.execute("INSERT INTO attributes (animal_id, attribute_id, attribute_name, publish) VALUES (%s, %s, %s, %s);", (animal['Internal-ID'], attr['Internal-ID'], attr['AttributeName'], attr['Publish']))
            except:
                print("No attributes found.")
            try:
                for photo in animal['Photos']:
                    cursor.execute("INSERT INTO photos (animal_id, url) VALUES (%s, %s);", (animal['Internal-ID'], photo))
            except:
                print("No photos found.")
            try:
                for video in animal['Videos']:
                    cursor.execute("INSERT INTO videos (animal_id, url) VALUES (%s, %s, %s);", (animal['Internal-ID'], video['EmbedUrl']))
            except:
                print("No videos found.")
    for a_id in dba:
        print("Updating animal id to adopted", a_id)
        """cursor.execute("DELETE FROM attributes WHERE animal_id = %s", ([a_id]))
        cursor.execute("DELETE FROM videos WHERE animal_id = %s", ([a_id]))
        cursor.execute("DELETE FROM photos WHERE animal_id = %s", ([a_id]))
        cursor.execute("DELETE FROM animal WHERE id = %s", ([a_id]))
        cursor.execute("DELETE FROM fees WHERE id = %s", ([a_id]))
        """
        cursor.execute('UPDATE animal SET status = "Adopted" WHERE id = %s', ([a_id]))


    conn.commit()
    cursor.close()
    conn.close()

updateAnimalDatabase()
