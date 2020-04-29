import React, { Component } from "react";
import "./App.css";
import Input from "./input/input";
import Upload from "./upload/Upload";
import PdfView from "./pdf/pdf_view";

class App extends Component {
  render() {
    return (
      <div className="App">
        <div className="Card">
          <Upload />
        </div>
        <div className="Card">
          <Input />
        </div>
      </div>
    );
  }
}

export default App;
