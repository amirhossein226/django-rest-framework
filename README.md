# A simple project using django rest framework
This is just simple project simulating sending OTP message to user for phone verification and login process:

## Setting up:
This are just some steps to making the project work on your system:

### Step 1: Clone The Project
use `git clone` command like below:
```
git clone https://github.com/amirhossein226/django-rest-framework.git
cd django-rest-framework
```

### Step 2: Install Dependencies
```
pip install -r requirements.txt
```

### Step 3: Migration
The project is using the default database(sqllite3), use below command to prepare database:
```
python3 manage.py makemigrations
python3 manage.py migrate
```

### Testing
You can use `curl` command to make request to the server, first start the server:
```
python3 manage.py runserver
```

There is some endpoints on this project which you can use:
```
localhost:8000/accounts/api/1.0/authenticate/ >>>> POST >>>> Need to include phone number
localhost:8000/accounts/api/1.0/verify_otp/ >>>> POST >>>> Need to include phone number from previous step and also OTP code
localhost:8000/accounts/api/1.0/user_credentials/ >>>> POST >>>> Need to include Phone number, first_name, last_name and email_address 
localhost:8000/accounts/api/1.0/verify_password/ >>>> POST >>>> Need to include Phone number and password 
```

#### Testing `localhost:8000/accounts/api/1.0/authenticate/` endpoint:
This endpoint gets the POST request including phone number.
A user with included phone number will created (If already it does not exist), and an OTP code will generate and associate to that user.
If the user with that phone number already exists then just the OTP code associated with it will be updated and returned.
This app, actually is meant to send the OTP code using SMS.But here for simplicity we are just printing it to terminal.

Lets test it:
```
curl -X POST -H 'Content-Type: application/json' -d '{"phone": "123456"}' localhost:8000/accounts/api/1.0/authenticate/
```

The result of above line will be like bellow:
```
{"message":"OTP code send to 123456!","user_was_exist":"false","otp_code":"717287"}
```

The message says that `"OTP code send to 123456"`, but as I said the OTP code will print on the terminal.
The part of response contains `"user_was_exists": "false"` is for informing the frontend developer about whether the user with  specified phone number previously was created in the database or not, in our case `false` indicate that the user was not created in the database (previously), but now it is created.

Run the previous command again:
```
curl -X POST -H 'Content-Type: application/json' -d '{"phone": "123456"}' localhost:8000/accounts/api/1.0/authenticate/
```
And you will get this:
```
{"message":"OTP code send to 123456!","user_was_exist":"true","otp_code":"965357"}
```
As you can see, The `"user_was_exist"` changed to `"true"`, also new `"otp_code"` generated.


#### Testing `localhost:8000/accounts/api/1.0/verify_otp/` endpoint:
You will use the phone number and OTP code from previous step to test this endpoint:
```
curl -X POST -H 'Content-Type: application/json' -d '{"phone": "123456", "otp": "502062"}' localhost:8000/accounts/api/1.0/verify_otp/
```

The result of above command will be like this:
```
{"message":"Verified Successfully"}
```

#### Testing `localhost:8000/accounts/api/1.0/user_credentials/` endpoint:
This endpoint receives phone number, first name, last name and also the  verified user's email and update its credentials"
```
curl -X POST -H 'Content-Type: application/json' -d '{"phone":"123456", "first_name": "Amir", "last_name": "sardari", "email": "amir226@gmail.com"}' localhost:8000/accounts/api/1.0/user_credentials/
```

Result:
```
{"message":"User credentials stored successfully!","credentials":{"first_name":"Amir","last_name":"sardari","phone":"123456","email":"amir226@gmail.com","created_at":"2025-04-21T08:20:33.234805Z","phone_verified":true}}

```
THis will give me us a `message` indicate the user credentials stored successfully and also some information about user credential that stored on database.