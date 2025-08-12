import React from "react";
import { Link, useLocation } from "react-router-dom";

export const Navbar = () => {
	const location = useLocation();

	const isActive = (path) => {
		return location.pathname === path;
	};

	return (
		<nav className="navbar">
			<div className="d-flex justify-content-between align-items-center w-100">
				<Link to="/" className="navbar-brand">
					<span className="cat-emoji">🐱</span>
					Finanzas Gatunas
				</Link>

				<div className="nav-pills">
					<Link
						to="/"
						className={`nav-link ${isActive('/') ? 'active' : ''}`}
					>
						<span>🏠</span>
						Dashboard
					</Link>
					<Link
						to="/transactions"
						className={`nav-link ${isActive('/transactions') ? 'active' : ''}`}
					>
						<span>💰</span>
						Transacciones
					</Link>
					<Link
						to="/categories"
						className={`nav-link ${isActive('/categories') ? 'active' : ''}`}
					>
						<span>📂</span>
						Categorías
					</Link>
					<Link
						to="/recurring"
						className={`nav-link ${isActive('/recurring') ? 'active' : ''}`}
					>
						<span>🔄</span>
						Pagos Recurrentes
					</Link>
					<Link
						to="/reports"
						className={`nav-link ${isActive('/reports') ? 'active' : ''}`}
					>
						<span>📊</span>
						Reportes
					</Link>
				</div>
			</div>
		</nav>
	);
};