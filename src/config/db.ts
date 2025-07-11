import mongoose from "mongoose";
require("dotenv").config();

const MONGO_URI = process.env.MONGO_URI;

const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGODB_URI as string)
        .then(() => {
            console.log('Connected to MongoDB');
        }).catch((error) => {
            console.error('Error connecting to MongoDB:', error);
        });
  } catch (error) {
    console.error("MongoDB connection error:", error);
    process.exit(1); 
  }
}

export default connectDB;