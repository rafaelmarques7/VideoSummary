import React from 'react';

class InputForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {value: ''};

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
    this.setState({value: event.target.value});
  }

  handleSubmit(event) {
    event.preventDefault();
    window.open(`/summary?youtube_url=${this.state.value}`)
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit}>
        <label>
          <input 
            type="text" 
            placeholder="Youtube video URL" 
            value={this.state.value} 
            onChange={this.handleChange} />
        </label>
        <input type="submit" value="Submit" />
      </form>
    );
  }
}

export default InputForm