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
    this.displayPdf = this.displayPdf.bind(this);
  }

  // componentDidMount() {
  //   axios
  //     .get(`http://127.0.0.1:5050/search`, {
  //       crossdomain: true,
  //       timeout: 80000,
  //       params: {
  //         "file-id": "zzzz_kwwbhpru77uc.pdf",
  //         keywords: this.reformatTags(),
  //       },
  //     })
  //     .then((response) => {
  //       this.setState({ searchingResultDocumentURL: response.data["result"] });
  //       console.log("reload");
  //     })
  //     .catch(function (error) {
  //       console.log("errrrrrr" + error);
  //     });
  // }
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

  sendTags() {
    axios
      .get(`http://127.0.0.1:5050/search`, {
        crossdomain: true,
        timeout: 80000,
        params: {
          "file-id":
            "/Users/admin/Downloads/chips-data-scraper-master/files/zzzz_kwwbhpru77uc.pdf",
          keywords: this.reformatTags(),
        },
      })
      .then((response) => {
        this.setState({ searchingResultDocumentURL: response.data["result"] });
        console.log(response.data["result"] + "send");
      })
      .catch(function (error) {
        console.log("er" + error);
      });
  }

  displayPdf() {
    return <PdfView kek="STM32_HAL_manual.pdf" />;
  }

  render() {
    console.log(this.state.searchingResultDocumentURL);
    const { tags, suggestions, placeholder } = this.state;
    return (
      <div className="Upload">
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
        <div>{this.displayPdf()}</div>
      </div>
    );
  }
}

export default Input;
