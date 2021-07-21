1. How is the logged in user being kept track of?

    we store the user's id inside of session[CURR_USER_KEY]

    before each request, we run @app.before_request
        we query for the specific User instance and set it equal to `g.user`
        now we can access that user's data globally throughout our app 

2. What is Flask's `g` object?

    Flask provides the `g` object for storing common data within the application context. 

    Anything we place into `g` will be cleared as soon as Flask sends a response.

    G stands for "global", but that is referring to the data being stored global within a context. The data on `g` is lost after the context(route) ends. 
    
    Use `session` or a database to store data across requests. `session` is also cryptographically secured (use of serialization and secret key)

3. What is the purpose of add_user_to_g?

    Assign the user to the g object. The purpose is so that we can use that data between different parts of our code base within the same request/response cycle.

    `g` is good for storing things that will be accessed by many parts of the app, like the current user. It is not passed back to the client.

4. What does @app.before_request mean?

    The decorator allows us to create functions that will run before each request.
    We use it if we want any specifc task to get executed before each request.

    In our app, if a user is logged in, it adds the user to the Flask global object.

