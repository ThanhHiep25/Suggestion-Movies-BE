// src/models/Movie.ts
import mongoose from 'mongoose';

// Định nghĩa Interface cho Movie Document
export interface IMovie extends mongoose.Document {
    plot?: string;
    genres?: string[];
    runtime?: number;
    rated?: string;
    cast?: string[];
    poster?: string;
    title?: string;
    fullplot?: string;
    languages?: string[];
    released?: Date;
    directors?: string[];
    writers?: string[];
    awards?: {
        wins?: number;
        nominations?: number;
        text?: string;
    };
    lastupdated?: Date;
    year?: number;
    imdb?: {
        rating?: number;
        votes?: number;
        id?: number;
    };
    countries?: string[];
    type?: string;
    tomatoes?: {
        viewer?: {
            rating?: number;
            numReviews?: number;
            meter?: number;
        };
        dvd?: Date;
        critic?: {
            rating?: number;
            numReviews?: number;
            meter?: number;
        };
        lastUpdated?: Date;
        rotten?: number;
        production?: string;
        fresh?: number;
    };
    num_mflix_comments?: number;
}

// Định nghĩa Movie Schema
const movieSchema = new mongoose.Schema<IMovie>({
    plot: String,
    genres: [String],
    runtime: Number,
    rated: String,
    cast: [String],
    poster: String,
    title: String,
    fullplot: String,
    languages: [String],
    released: Date,
    directors: [String],
    writers: [String],
    awards: {
        wins: Number,
        nominations: Number,
        text: String
    },
    lastupdated: Date,
    year: Number,
    imdb: {
        rating: Number,
        votes: Number,
        id: Number
    },
    countries: [String],
    type: String,
    tomatoes: {
        viewer: {
            rating: Number,
            numReviews: Number,
            meter: Number
        },
        dvd: Date,
        critic: {
            rating: Number,
            numReviews: Number,
            meter: Number
        },
        lastUpdated: Date,
        rotten: Number,
        production: String,
        fresh: Number
    },
    num_mflix_comments: Number
}, { collection: 'embedded_movies' }); 

const Movie = mongoose.model<IMovie>('Movie', movieSchema);
export default Movie;