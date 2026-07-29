import styles from "./MembershipCard.module.css";
import PropTypes from 'prop-types'; 

const MembershipCard = ({type, detail, price}) => {
	return (
		<div className={styles.container}>
			<h4>{type}</h4>
			<p>${price}</p>
			<p>incluye:</p>
			<p>{detail}</p>
		</div>
	)
}

MembershipCard.propTypes = {
	type : PropTypes.string.isRequired,
	detail : PropTypes.string.isRequired,
	price: PropTypes.number.isRequired,
}

export default MembershipCard;
