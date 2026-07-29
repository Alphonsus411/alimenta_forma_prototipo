import { useCallback } from "react";
import Header from "../components/Header";
import Title from "../components/Title";
import MembershipCard from "../components/MembershipCard";
import AsyncState from "../components/AsyncState";
import useRemoteResource from "../hooks/useRemoteResource";
import { getMemberships } from "../services/membershipsApi";

const Membership = () => {

	const loadMemberships = useCallback(() => getMemberships(), []);
	const { data: memberships, error, loading, reload } = useRemoteResource(loadMemberships);

	return (
		<div>
			<Header />
			<Title text="Nuestros Precios" />
			<AsyncState loading={loading} error={error} empty={memberships?.length === 0} emptyMessage="No hay membresías disponibles." onRetry={reload}>
				<section aria-label="Membresías disponibles">
					{memberships?.map((membership) => (
						<MembershipCard key={membership.id} type={membership.category_name || `Categoría #${membership.userType}`} detail={membership.detail} price={membership.price} />
					))}
				</section>
			</AsyncState>
		</div>
	)
}

export default Membership;
