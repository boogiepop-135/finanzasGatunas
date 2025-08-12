export const Footer = () => (
	<footer style={{
		background: 'linear-gradient(90deg, var(--primary-pink) 0%, var(--dark-pink) 100%)',
		color: 'white',
		padding: 'var(--spacing-4)',
		textAlign: 'center',
		marginTop: 'auto'
	}}>
		<div className="d-flex justify-content-center align-items-center gap-2 mb-2">
			<span>🐱</span>
			<p className="mb-0">
				Finanzas Gatunas - Gestiona tu dinero como un gato inteligente
			</p>
			<span>💰</span>
		</div>
		<p className="mb-0" style={{ fontSize: 'var(--font-size-sm)', opacity: 0.8 }}>
			Hecho con <span style={{ color: 'var(--cream)' }}>💖</span> y mucho <span style={{ color: 'var(--cream)' }}>☕</span>
		</p>
	</footer>
);
