import mongoose from "mongoose";
require("dotenv").config();

const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGODB_URI as string, {
      serverSelectionTimeoutMS: 5000, // Thử timeout 5 giây
      socketTimeoutMS: 45000, // Thử socket timeout 45 giây
    });
    console.log("Connected to MongoDB");
  } catch (error) {
    // Lỗi sẽ được bắt ở đây nếu mongoose.connect thất bại
    console.error("MongoDB connection error:", error);
    // process.exit(1); // Giữ lại dòng này để thoát ứng dụng nếu không kết nối được DB
  }
};

export default connectDB;
