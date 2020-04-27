import React from "react";
import ReactDOM from "react-dom";
import { WithContext as ReactTags } from "react-tag-input";
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
      placeholder: "add component name",
      placeholder1: "add searching tags",
      suggestions: [],
    };
    this.handleDelete = this.handleDelete.bind(this);
    this.handleAddition = this.handleAddition.bind(this);
    this.handleModelChange = this.handleModelChange.bind(this);
    this.sendTags = this.sendTags.bind(this);
    this.reformatTags = this.reformatTags.bind(this);
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

  sendTags() {
    axios
      .get(`http://127.0.0.1:5050/search`, {
        params: {
          "file-id": "456789",
          componentName: this.state.model,
          keywords: this.reformatTags(),
        },
      })
      .then((response) => {
        console.log(response.data);
        console.log(response.status);
        console.log(response.statusText);
        console.log(response.headers);
        console.log(response.config);
      });
  }

  render() {
    const { tags, suggestions, placeholder } = this.state;
    return (
      <div className="Upload">
        <form onSubmit={this.sendTags}>
          <input
            class="ReactTags__tagInputField"
            type="text"
            placeholder="fill component name here"
            aria-label="add"
            value={this.state.model}
            onChange={this.handleModelChange}
          ></input>
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
      </div>
    );
  }
}

export default Input;
