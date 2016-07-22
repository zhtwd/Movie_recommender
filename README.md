# Movie recommendation server
----------------------------

### There are 3 end points
##### `POST /follow`
Add one follow relationship (see `follows.json`)

the request body have 2 params:
- from: \<user ID\>
- to: \<user ID\>

##### `POST /watch`
Add one movie as the user has just watched ( see `watch.json` )

the request body have 2 params:
- user: \<user ID\>
- music: \<music ID\>

##### `GET /recommendations`
Return 5 music recommendations to this user, they should be sorted by relevance

Query string has:
- user: \<user ID\>

response looks like:

```json
{
  "list": ["<movie ID>", "<movie ID>", "<movie ID>", "<movie ID>", "<movie ID>"]
}
```

## Algorithm
------------
The movies are ranked using the following three acpects.

1. User cosine similarity based on the watching history.

2. Boost the score of movies watched by the following user.

3. Boost the score of movies using cosine similarity based on genres.


Finally, one or two movies the user watched the most will be recommended along with the top ones from the movie ranking logic.

## Installation
---------------
Please use Python 2.7.11.

```Python
python -r requirements.txt
```

## Testing
----------
The testing framework tests the following instructions.
+ feed the follows.json through your /follow endpoint, in sequence
+ he same for /watch
+ make a call to user "a" on /recommendations and display the result
```Python
python script.py
```

## Run the server
------
```bash
sh run.sh
```

