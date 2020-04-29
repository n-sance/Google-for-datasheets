import React from "react";
import ReactDOM from "react-dom";
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
      placeholder: "add component name",
      placeholder1: "add searching tags",
      suggestions: [],
    };
    this.handleDelete = this.handleDelete.bind(this);
    this.handleAddition = this.handleAddition.bind(this);
    this.handleModelChange = this.handleModelChange.bind(this);
    this.sendTags = this.sendTags.bind(this);
    this.reformatTags = this.reformatTags.bind(this);
    this.displayPdf = this.displayPdf.bind(this);
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

  async getDataFetch() {
    const response = await fetch(`http://127.0.0.1:5050/search`, {
      headers: { "Content-Type": "application/json" },
    });
    console.log(await response.json());
  }

  async sendTags() {
    try {
      console.log("lllllllllllll");
      let r = await axios.get(`http://127.0.0.1:5050/search`, {
        timeout: 80000,
        params: {
          "file-id": "some_id",
          keywords: this.reformatTags(),
        },
      });
      this.setState({ searchingResultDocumentURL: "ff" });
      console.log(r.headers);
    } catch (error) {
      console.log(error);
      this.setState({ searchingResultDocumentURL: "ff" });
    }
  }

  displayPdf() {
    if (this.state.searchingResultDocumentURL) {
      return <PdfView />;
    }
    return null;
  }

  render() {
    const { tags, suggestions, placeholder } = this.state;
    return (
      <div className="Upload">
        <form onSubmit={this.getDataFetch}>
          <div className="Actions">
            <button type="submit" value="Отправить">
              Send
            </button>
          </div>
        </form>
        <ReactTags
          tags={tags}
          placeholder={placeholder}
          suggestions={suggestions}
          handleDelete={this.handleDelete}
          handleAddition={this.handleAddition}
          delimiters={delimiters}
        />
        <div>{this.displayPdf()}</div>
      </div>
    );
  }
}

export default Input;
