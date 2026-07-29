import PropTypes from "prop-types";

const AsyncState = ({ loading, error = null, empty = false, emptyMessage, onRetry, children = null }) => {
  if (loading) return <p role="status" aria-live="polite">Cargando…</p>;
  if (error) {
    return (
      <div role="alert">
        <p>{error.message || "No se pudieron cargar los datos."}</p>
        <button type="button" onClick={onRetry}>Reintentar</button>
      </div>
    );
  }
  if (empty) return <p role="status">{emptyMessage}</p>;
  return children;
};

AsyncState.propTypes = {
  loading: PropTypes.bool.isRequired,
  error: PropTypes.instanceOf(Error),
  empty: PropTypes.bool,
  emptyMessage: PropTypes.string.isRequired,
  onRetry: PropTypes.func.isRequired,
  children: PropTypes.node,
};

export default AsyncState;
