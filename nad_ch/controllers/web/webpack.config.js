const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");

module.exports = {
  mode: "development",
  entry: {
    main: ["./src/index.ts", "./sass/index.scss"],
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: "ts-loader",
        exclude: /node_modules/,
      },
      {
        test: /\.s[ac]ss$/i,
        use: [
          { loader: MiniCssExtractPlugin.loader },
          { loader: "css-loader", options: { url: false, sourceMap: true } },
          {
            loader: "postcss-loader",
            options: {
              sourceMap: true,
            },
          },
          {
            loader: "sass-loader",
            options: {
              implementation: require("node-sass"),
              sourceMap: true,
              sassOptions: {
                includePaths: [
                  path.resolve(__dirname, "node_modules"),
                  path.resolve(__dirname, "node_modules/uswds/dist/scss"),
                  path.resolve(__dirname, "node_modules/uswds/dist/fonts"),
                ],
              },
            },
          },
        ],
      },
      {
        test: /\.css$/,
        include: [path.resolve(__dirname, "node_modules/@uswds/uswds")],
        use: [MiniCssExtractPlugin.loader, "css-loader"],
      },
    ],
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: "style.css",
    }),
    new CopyWebpackPlugin({
      patterns: [
        {
          from: path.resolve(__dirname, "images"),
          to: path.resolve(__dirname, "dist"),
          noErrorOnMissing: true,
        },
      ],
    }),
  ],
  resolve: {
    extensions: [".tsx", ".ts", ".js", ".scss"],
    alias: {
      uswds: path.resolve(__dirname, "node_modules/@uswds/uswds"),
    },
  },
  output: {
    filename: "bundle.js",
    path: path.resolve(__dirname, "dist"),
  },
};
