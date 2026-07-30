import { Component } from 'react';
import PropTypes from 'prop-types';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  handleReset = () => {
    this.props.onReset?.();
    this.setState({ hasError: false });
  };

  render() {
    if (this.state.hasError) {
      return (
        <main className="routeFeedback" role="alert">
          <h1>Algo no ha salido bien</h1>
          <p>Se ha producido un error inesperado. Puedes intentar recuperar la página de forma segura.</p>
          <button type="button" onClick={this.handleReset}>Intentar de nuevo</button>
        </main>
      );
    }

    return this.props.children;
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired,
  onReset: PropTypes.func,
};

ErrorBoundary.defaultProps = {
  onReset: undefined,
};

export default ErrorBoundary;
