import React from "react";
//import ReactDOM from "react-dom";
import { WithContext as ReactTags } from "react-tag-input";
import PdfView from "../pdf/pdf_view";
import axios from "axios";
const KeyCodes = {
  comma: 188,
  enter: 13,
};

const delimiters = [KeyCodes.comma, KeyCodes.enter];

class Input extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      tags: [],
      model: "",
      temp: "",
      searchingResultDocumentURL: "",
      placeholder: "add searching tags here",
      placeholder1: "add searching tags",
      suggestions: [],
    };
    this.handleDelete = this.handleDelete.bind(this);
    this.handleAddition = this.handleAddition.bind(this);
    this.handleModelChange = this.handleModelChange.bind(this);
    this.sendTags = this.sendTags.bind(this);
    this.reformatTags = this.reformatTags.bind(this);
    //this.displayPdf = this.displayPdf.bind(this);
  }

  handleDelete(i) {
    const { tags } = this.state;
    this.setState({
      tags: tags.filter((tag, index) => index !== i),
    });
  }

  handleAddition(tag) {
    this.setState((state) => ({ tags: [...state.tags, tag] }));
  }

  handleModelChange(event) {
    this.setState({ model: event.target.value });
  }

  reformatTags() {
    var out = [];
    var result = "";
    this.state.tags.forEach(function tk(val) {
      out.push(val["id"]);
    });
    result = out.join(";");
    return result;
  }

  sendTags = () => {
    var url = new URL("http://127.0.0.1:5050/search"),
      params = {
        "component-name": this.state.model,
        "all-docs-search": true,
        keywords: this.reformatTags(),
      };
    Object.keys(params).forEach((key) =>
      url.searchParams.append(key, params[key])
    );
    fetch(url).then((response) => {
      response.blob().then((blob) => {
        let url = window.URL.createObjectURL(blob);
        console.log("link is:  " + url);
        this.setState({ searchingResultDocumentURL: url });
        console.log("state is:      " + url);
        const a = document.createElement("a");
        a.href = url;
        a.setAttribute("download", "file.pdf");
        document.body.appendChild(a);
        a.click();
      });
      //window.location.href = response.url;
    });
  };
  handleModelChange(event) {
    this.setState({ model: event.target.value });
  }
  // displayPdf() {
  //   return <PdfView kek="STM32_HAL_manual.pdf" />;
  // }

  render() {
    console.log(this.state.searchingResultDocumentURL);
    const { tags, suggestions, placeholder } = this.state;
    return (
      <div className="Upload">
        <div className="Input">
          <input
            className="ReactTags__tagInputField"
            type="text"
            placeholder="fill component name here"
            aria-label="add"
            value={this.state.model}
            onChange={this.handleModelChange}
          ></input>
        </div>
        <div className="Actions">
          <button onClick={this.sendTags}>Search</button>
        </div>
        <ReactTags
          tags={tags}
          placeholder={placeholder}
          suggestions={suggestions}
          handleDelete={this.handleDelete}
          handleAddition={this.handleAddition}
          delimiters={delimiters}
        />
      </div>
    );
  }
}

export default Input;
