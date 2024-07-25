This project uses Python and has three main parts.

We first build a Pokemon database (Pokedex) using web-scraping, Beautiful Soup, and PyMongo. All data is extracted from pokemondb.net and MongoDB is used to store the data.

Next, we use speech recognition and fuzzy searching to compare user speech input with the best match in our Pokedex.

Using AWS Polly and PyAudio, we perform text-to-speech on that match and relay the Pokemon name back to the user.
