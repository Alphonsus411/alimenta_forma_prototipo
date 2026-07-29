import { useCallback, useState } from "react";
import Header from "../components/Header";
import ProfileFooter from "../components/ProfileFooter";
import Title from "../components/Title";
import AsyncState from "../components/AsyncState";
import useRemoteResource from "../hooks/useRemoteResource";
import { getProfile, updateProfile } from "../services/profileApi";

const Profile = () => {
	const loadProfile = useCallback(() => getProfile(), []);
	const { data, error, loading, reload, setData } = useRemoteResource(loadProfile);
	const [saving, setSaving] = useState(false);
	const [saveError, setSaveError] = useState("");
	const [saved, setSaved] = useState(false);

	const handleSubmit = async (event) => {
		event.preventDefault();
		setSaving(true);
		setSaveError("");
		setSaved(false);
		const form = new FormData(event.currentTarget);
		try {
			const profile = await updateProfile(data.profile.id, {
				location: form.get("location"),
				phone: form.get("phone"),
				description: form.get("description"),
			});
			setData({ ...data, profile });
			setSaved(true);
		} catch (submitError) {
			setSaveError(submitError.message || "No se pudo actualizar el perfil.");
		} finally {
			setSaving(false);
		}
	};

	return (
		<div>
			<Header />
			<Title text="Mi perfil" />
			<AsyncState loading={loading} error={error} empty={data?.profile === null} emptyMessage="Tu usuario todavía no tiene un perfil." onRetry={reload}>
				{data?.profile && (
					<section aria-label="Datos del perfil">
						<h2>{data.user.first_name} {data.user.last_name}</h2>
						<p>@{data.user.username} · {data.user.email}</p>
						<form onSubmit={handleSubmit}>
							<label htmlFor="profile-location">Ciudad</label>
							<input id="profile-location" name="location" defaultValue={data.profile.location} />
							<label htmlFor="profile-phone">Teléfono</label>
							<input id="profile-phone" name="phone" defaultValue={data.profile.phone} />
							<label htmlFor="profile-description">Descripción</label>
							<textarea id="profile-description" name="description" defaultValue={data.profile.description} />
							<button type="submit" disabled={saving}>{saving ? "Guardando…" : "Guardar perfil"}</button>
						</form>
						{saveError && <p role="alert">{saveError}</p>}
						{saved && <p role="status">Perfil actualizado.</p>}
					</section>
				)}
			</AsyncState>
			<ProfileFooter />
		</div>
	)
}

export default Profile;
