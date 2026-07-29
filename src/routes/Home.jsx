import { useCallback } from "react";
import Header from "../components/Header";
import Announcement from "../components/Announcement";
import InitButtons from "../components/InitButtons";
import AsyncState from "../components/AsyncState";
import useRemoteResource from "../hooks/useRemoteResource";
import { getAnnouncements } from "../services/announcementsApi";

const Home = () => {
	const loadAnnouncements = useCallback(() => getAnnouncements(), []);
	const { data: announcements, error, loading, reload } = useRemoteResource(loadAnnouncements);
	return (
		<>
			<Header />
			<AsyncState loading={loading} error={error} empty={announcements?.length === 0} emptyMessage="No hay anuncios publicados." onRetry={reload}>
				<section aria-label="Anuncios">
					{announcements?.map((announcement) => <Announcement key={announcement.id} announcement={announcement} />)}
				</section>
			</AsyncState>
			<InitButtons />
		</>
	)
}

export default Home;
