#!/usr/bin/env python
# coding: utf-8

# # Data Engineering Project
# 
# #### We need to, first, do the Python ETL, and afterwards, map it into a RELATIONAL DATABASE using PonyORM

# A SMB (small-to-medium business) has recently begun to utilise the data they obtain from
# their customers. Unfortunately, their business has multiple areas which all have customer
# data specific to that area, and this is fragmented within the organisation. E.g Credit Card
# data is only stored by the financial systems, employment within HR, etc. There is not a single
# cohesive record representing customers. <br>
# 
# The SMB is looking to unify these ahead of further data investigation, and to pool all this data together into a central datastore.
# The data provided for this assessment is mock data representing a typical customer-facing
# business; these involve data such as names, banking credentials, family attributes, etc.
# These data files are provided as a mixed modality in a variety of formats (CSV, JSON, XML,
# and TXT).<br>
# 
# The work herein requires the processing of these data into a homogenous record, aligning
# the same customers from different sources together, which are then automatically entered
# into a Relational Database System using modern tools & libraries. <br>
# 
# You are expected to read and extract data from these various formats, wrangle the data -
# solving inconsistencies if present - and bring data together into a singular format. <br>
# 
# These unified records are then to be mapped to a relational database
# using PonyORM Entities, with all unified records being entered into the database

# ### Reading all four data files provided for this assignment

# ##### Importing essential libraries

# In[3]:


import pandas as pd
import numpy as np
from lxml import objectify


# #### 1. Reading from CSV file, first

# In[4]:


df_csv = pd.read_csv("user_data.csv")
df_csv.rename(columns={"First Name": "first_name", "Second Name": "last_name", 
"Age (Years)":"age","Sex":"sex", "Vehicle Make": "vehicle_make","Vehicle Model":"vehicle_model",
"Vehicle Year":"vehicle_year","Vehicle Type": "vehicle_type"},inplace=True)


# In[5]:


df_csv.head()


# In[6]:


df_csv.info()


# ##### Reading from JSON file

# In[7]:


## As our data in JSON file doesn't need to normalized, we can straightawy use it to convert to df
df_json = pd.read_json("user_data.json")
df_json.rename(columns={"firstName": "first_name", "lastName": "last_name"},inplace=True)


# In[8]:


df_json.head()


# In[9]:


df_json.info()


# In[10]:


#Filling NaN in debt as 0 in df_json
df_json['debt'] = df_json['debt'].replace(np.nan, 0)
#re-checking the head of df_json
df_json.head()


# In[11]:


df_json.info()


# ##### Reading from text file

# In[12]:


with open('user_data.txt') as f:
    for line in f:
        print(line)


# ##### Reading from XML file

# In[13]:


df_xml = pd.read_xml('user_data.xml')
df_xml.rename(columns={"firstName": "first_name", "lastName": "last_name"},inplace=True)


# In[14]:


df_xml


# In[15]:


df_xml.info()


# In[16]:


#Here, in df_xml, we have two columns with NaN, dependants and company; dependents NaN can be changed to 0. 
#With company name, it would be suitable to change it to "Unknown" than numeric 0
df_xml['dependants'] = df_xml['dependants'].replace(np.nan, 0)
df_xml['company'] = df_xml['company'].replace(np.nan,"Unknown")


# In[17]:


#Re-checking df_xml for the alterations made
df_xml.head()


# In[18]:


df_xml.info()


# ### Changing certain information in DATAFRAMES created as per the instruction given in the text file.

# ###### First, to update security code of user Debra Wood to 592. 
# ###### Second, to increase Howard salary by 2000
# ###### Third, to update Molly Dobson age to 82. 
# ###### Fourth, to update pension figure to maximum of £27334 or £25901 for Mr. Miller

# In[19]:


#First:
# changing credit_card_security_code in df_json to 592 for Debra Wood
df_json.loc[(df_json.first_name == 'Debra') & (df_json.last_name == 'Wood'), ['credit_card_security_code']] = 592


# In[20]:


#Second:
#increasing Howard salary by 2000
df_xml.loc[df_xml.first_name == "Howard", 'salary'] += 2000


# In[21]:


#Third:
# updating age of Molly Dobson to 82
df_xml.loc[(df_xml.first_name == 'Molly') & (df_xml.last_name == 'Dobson'), ['age']] = 82
df_json.loc[(df_json.first_name == 'Molly') & (df_json.last_name == 'Dobson'), ['age']] = 82
df_csv.loc[(df_csv.first_name == 'Molly') & (df_csv.last_name == 'Dobson'), ['age']] = 82


# In[22]:


#Fourth:
#updating pension figure to 27334 for Mr. Miller
df_xml.loc[(df_xml.last_name == 'Miller'), ['pension']] = 27334


# In[23]:


df_csv.head()


# In[24]:


df_json.head()


# In[25]:


df_xml.head()


# ### Merging all three different datframes
# 1. First, merging ``df_csv`` and ``df_xml`` on the ``first_name``, ``last_name``, ``age``, and ``sex`` as these are the common column in both of them.<br>
# 2. Thereafter, merging the obtained result with the ``df_json`` on ``first_name``, ``last_name``, ``address_postcode``, and ``age`` columns as ``df_json`` doesn't have sex column in it

# In[26]:


result = pd.merge(df_csv, df_xml, on=["first_name","last_name","age","sex"])
result = pd.merge(result,df_json, on=["first_name","last_name","age", "address_postcode"])
result


# ###### We should make a column "full_name" as in database it could be the most suitable column to actually work as a primary key. "credit_card" numbers are unique and logically work as primary key for identifier, however, what if a customer is smart, and dont want liabilities, and thus declining credit card offer. Is it unethical too to segment people with their credit card number?

# In[27]:


#Creating a new column "full_name"
result['full_name'] = result['first_name'] + ' ' + result['last_name']
#chaning order of column to bring "full_name" ahead from the end
cols = ['first_name','last_name','full_name']
result = result[cols + [c for c in result.columns if c not in cols]]
result


# In[28]:


result.info()


# ## NOW, Working with PONY ORM

# Re-running this section will try to create instance all over again, so not running it again.

# In[29]:


from pony.orm import *
from pony import orm


# In[30]:


db = Database()


# In[ ]:


class Client(db.Entity):
    first_name = Required(str)
    last_name = Required(str)
    full_name = PrimaryKey(str) #As is is primary key, needed to be unique=True
    age = Required(int)
    sex = Optional(str)
    vehicle_make = Required(str)
    vehicle_model = Required(str)
    vehicle_year = Required(int)
    vehicle_type = Optional(str) #This can be done optional
    retired = Required(bool) #As it is just True/False
    dependants = Required(int)
    marital_status = Required(str)
    salary = Required(int)
    pension = Required(int)
    company = Required(str)
    commute_distance = Optional(float)
    address_postcode = Required(str)
    iban = Required(str, unique=True) #As it is a unique indentifier to a client
    credit_card_number = Required(int, unique=True) # This is too an unique identifier
    credit_card_security_code = Required(int, unique=True) #Same for this
    credit_card_start_date  = Required(str)
    credit_card_end_date = Required(str)
    address_main = Optional(str) #As address_postcode is enough for an indentifier
    address_city = Optional(str) #As address_postcode is enough for an identifier 
    debt = Required(str)


# In[33]:


#Establishing connection with the PhpMtAdmin on the host "europa.ashley.work"

db.bind(provider='mysql', host='europa.ashley.work', user='student_bh95bi', passwd='iE93F2@8EhM@1zhD&u9M@K', db='student_bh95bi')


# In[34]:


db.generate_mapping(create_tables=True)


# In[35]:


set_sql_debug(True)


# In[36]:


Client.select().show()


# In[ ]:


with db_session:
    result.to_sql("Client", db.get_connection())
    print db.select("COUNT (*) FROM Client")    
    

