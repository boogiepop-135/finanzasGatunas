import React, { useState, useEffect } from "react";

const Categories = () => {
    const [categories, setCategories] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [editingCategory, setEditingCategory] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        color: '#FF69B4',
        icon: '🐱'
    });

    const suggestedIcons = [
        '🐱', '😸', '😺', '🙀', '😿', '😾', // Gatos
        '🍕', '🍔', '🍟', '🥗', '🍜', '🥘', // Comida
        '🏠', '🏡', '🏢', '🏪', '🏫', '⛽', // Lugares
        '🚗', '🚕', '🚌', '🚇', '✈️', '🚲', // Transporte
        '👕', '👖', '👗', '👠', '👜', '💄', // Ropa
        '🎬', '🎮', '🎵', '📚', '🎨', '⚽', // Entretenimiento
        '💊', '🏥', '💉', '🩺', '😷', '🧴', // Salud
        '💰', '💳', '🏦', '💎', '📊', '📈', // Finanzas
        '🛒', '🛍️', '🎁', '💝', '🧸', '🎀'  // Compras
    ];

    const suggestedColors = [
        '#FF69B4', '#FFB6C1', '#DDA0DD', '#F0E68C',
        '#98FB98', '#87CEEB', '#FFA07A', '#FFE4E1',
        '#E6E6FA', '#FFFACD', '#F5FFFA', '#FFE4B5'
    ];

    useEffect(() => {
        fetchCategories();
    }, []);

    const fetchCategories = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/categories`);
            if (response.ok) {
                const data = await response.json();
                setCategories(data);
            }
        } catch (error) {
            console.error("Error fetching categories:", error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        const url = editingCategory
            ? `${import.meta.env.VITE_BACKEND_URL}/api/categories/${editingCategory.id}`
            : `${import.meta.env.VITE_BACKEND_URL}/api/categories`;

        const method = editingCategory ? 'PUT' : 'POST';

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                await fetchCategories();
                handleCloseModal();
            }
        } catch (error) {
            console.error("Error saving category:", error);
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('¿Estás seguro de que quieres eliminar esta categoría?')) {
            try {
                const response = await fetch(
                    `${import.meta.env.VITE_BACKEND_URL}/api/categories/${id}`,
                    { method: 'DELETE' }
                );

                if (response.ok) {
                    await fetchCategories();
                }
            } catch (error) {
                console.error("Error deleting category:", error);
            }
        }
    };

    const handleEdit = (category) => {
        setEditingCategory(category);
        setFormData({
            name: category.name,
            description: category.description || '',
            color: category.color,
            icon: category.icon
        });
        setShowModal(true);
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setEditingCategory(null);
        setFormData({
            name: '',
            description: '',
            color: '#FF69B4',
            icon: '🐱'
        });
    };

    const createDefaultCategories = async () => {
        const defaultCategories = [
            { name: 'Alimentación', description: 'Comida y bebidas', color: '#FF69B4', icon: '🍕' },
            { name: 'Transporte', description: 'Gasolina, transporte público', color: '#87CEEB', icon: '🚗' },
            { name: 'Hogar', description: 'Servicios públicos, alquiler', color: '#98FB98', icon: '🏠' },
            { name: 'Entretenimiento', description: 'Cine, juegos, diversión', color: '#DDA0DD', icon: '🎮' },
            { name: 'Salud', description: 'Médico, medicinas', color: '#FFB6C1', icon: '💊' },
            { name: 'Compras', description: 'Ropa, accesorios', color: '#F0E68C', icon: '🛒' },
            { name: 'Ingresos', description: 'Salario, bonos', color: '#90EE90', icon: '💰' },
            { name: 'Otros', description: 'Gastos varios', color: '#FFA07A', icon: '📦' }
        ];

        for (const category of defaultCategories) {
            try {
                await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/categories`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(category),
                });
            } catch (error) {
                console.error("Error creating default category:", error);
            }
        }

        await fetchCategories();
    };

    return (
        <div className="content-container fade-in">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h1>
                    <span>📂</span>
                    Categorías
                </h1>
                <div className="d-flex gap-2">
                    {categories.length === 0 && (
                        <button
                            className="btn btn-secondary"
                            onClick={createDefaultCategories}
                        >
                            <span>🎯</span>
                            Crear Categorías por Defecto
                        </button>
                    )}
                    <button
                        className="btn btn-primary"
                        onClick={() => setShowModal(true)}
                    >
                        <span>➕</span>
                        Nueva Categoría
                    </button>
                </div>
            </div>

            {/* Estadísticas de categorías */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon">📂</div>
                    <span className="stat-value">
                        {categories.length}
                    </span>
                    <div className="stat-label">Total Categorías</div>
                </div>
            </div>

            {/* Lista de categorías */}
            <div className="card">
                <div className="card-header">
                    <h4>📋 Gestión de Categorías</h4>
                </div>
                <div className="card-body">
                    {categories.length === 0 ? (
                        <div className="text-center p-5">
                            <div style={{ fontSize: '4rem' }}>😿</div>
                            <h5>No hay categorías creadas</h5>
                            <p>¡Crea categorías para organizar mejor tus finanzas!</p>
                        </div>
                    ) : (
                        <div className="row">
                            {categories.map((category) => (
                                <div key={category.id} className="col-md-6 col-lg-4 mb-4">
                                    <div className="card h-100" style={{ borderLeft: `4px solid ${category.color}` }}>
                                        <div className="card-body">
                                            <div className="d-flex justify-content-between align-items-start mb-3">
                                                <div
                                                    className="transaction-icon"
                                                    style={{ backgroundColor: category.color }}
                                                >
                                                    {category.icon}
                                                </div>
                                                <div className="d-flex gap-2">
                                                    <button
                                                        className="btn btn-sm btn-secondary"
                                                        onClick={() => handleEdit(category)}
                                                    >
                                                        ✏️
                                                    </button>
                                                    <button
                                                        className="btn btn-sm btn-danger"
                                                        onClick={() => handleDelete(category.id)}
                                                    >
                                                        🗑️
                                                    </button>
                                                </div>
                                            </div>

                                            <h6 className="card-title">{category.name}</h6>
                                            {category.description && (
                                                <p className="card-text text-muted small">
                                                    {category.description}
                                                </p>
                                            )}

                                            <div className="d-flex align-items-center gap-2 mt-3">
                                                <div
                                                    style={{
                                                        width: '20px',
                                                        height: '20px',
                                                        backgroundColor: category.color,
                                                        borderRadius: '50%'
                                                    }}
                                                ></div>
                                                <small className="text-muted">{category.color}</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Modal para agregar/editar categoría */}
            {showModal && (
                <div className="modal-overlay" onClick={handleCloseModal}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h5>
                                {editingCategory ? '✏️ Editar Categoría' : '➕ Nueva Categoría'}
                            </h5>
                            <button
                                className="btn btn-sm btn-secondary"
                                onClick={handleCloseModal}
                            >
                                ❌
                            </button>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div className="modal-body">
                                <div className="form-group">
                                    <label className="form-label">Nombre</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        value={formData.name}
                                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                        placeholder="Nombre de la categoría"
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Descripción</label>
                                    <textarea
                                        className="form-control"
                                        value={formData.description}
                                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                        placeholder="Descripción opcional..."
                                        rows="3"
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Icono</label>
                                    <div className="d-flex align-items-center gap-3 mb-3">
                                        <div
                                            className="transaction-icon"
                                            style={{ backgroundColor: formData.color }}
                                        >
                                            {formData.icon}
                                        </div>
                                        <input
                                            type="text"
                                            className="form-control"
                                            value={formData.icon}
                                            onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
                                            placeholder="Selecciona un emoji"
                                            maxLength="2"
                                            style={{ width: '100px' }}
                                        />
                                    </div>
                                    <div className="d-flex flex-wrap gap-2">
                                        {suggestedIcons.map((icon, index) => (
                                            <button
                                                key={index}
                                                type="button"
                                                className="btn btn-sm btn-secondary"
                                                onClick={() => setFormData({ ...formData, icon })}
                                                style={{ fontSize: '1.2rem' }}
                                            >
                                                {icon}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Color</label>
                                    <div className="d-flex align-items-center gap-3 mb-3">
                                        <input
                                            type="color"
                                            className="form-control"
                                            value={formData.color}
                                            onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                                            style={{ width: '60px', height: '40px' }}
                                        />
                                        <input
                                            type="text"
                                            className="form-control"
                                            value={formData.color}
                                            onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                                            placeholder="#FF69B4"
                                        />
                                    </div>
                                    <div className="d-flex flex-wrap gap-2">
                                        {suggestedColors.map((color, index) => (
                                            <button
                                                key={index}
                                                type="button"
                                                className="btn btn-sm"
                                                onClick={() => setFormData({ ...formData, color })}
                                                style={{
                                                    backgroundColor: color,
                                                    width: '30px',
                                                    height: '30px',
                                                    border: '2px solid #ddd'
                                                }}
                                            />
                                        ))}
                                    </div>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" onClick={handleCloseModal}>
                                    Cancelar
                                </button>
                                <button type="submit" className="btn btn-primary">
                                    {editingCategory ? 'Actualizar' : 'Guardar'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Categories;
