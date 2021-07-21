1. How is the logged in user being kept track of?

    using session[CURR_USER_KEY]

2. What is Flask's `g` object?

    Flask provides the `g` object for storing common data within the application context. It is a simple namespace object that has the same lifetime as an application context. 

    G stands for "global", but that is referring to the data being stored global within a context. The data on `g` is lost after the context ends, and it is not an appropriate place to store data between requests. 
    
    Use `session` or a database to store data across requests. `session` is also cryptographically secured (use of serialization and secret key)

3. What is the purpose of add_user_to_g?

    Assign the user to the g object. The purpose is so that we can use that data between different parts of our code base if it's within the same request cycle.

    Anything we place into `g` will be cleared as soon as Flask sends a response.
    `g` is good for storing things that will be accessed by many parts of the app, like the current user. It is not passed back to the client, and exists only internally as a helper object for Flask.

4. What does @app.before_request mean?

    The decorator allows us to create functions that will run before each request.
    We use it if we want any specifc task to get executed before each request.

    In our app, if a user is logged in, it adds the user to the Flask global object.
