import React, { useState, useEffect } from "react";
import { format, addDays, addWeeks, addMonths, addYears } from 'date-fns';
import { es } from 'date-fns/locale';

const RecurringPayments = () => {
    const [recurringPayments, setRecurringPayments] = useState([]);
    const [categories, setCategories] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [editingPayment, setEditingPayment] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        amount: '',
        description: '',
        frequency: 'monthly',
        next_payment_date: new Date().toISOString().split('T')[0],
        category_id: '',
        is_active: true
    });

    const frequencyOptions = [
        { value: 'daily', label: '📅 Diario', icon: '📅' },
        { value: 'weekly', label: '📆 Semanal', icon: '📆' },
        { value: 'monthly', label: '🗓️ Mensual', icon: '🗓️' },
        { value: 'yearly', label: '📋 Anual', icon: '📋' }
    ];

    useEffect(() => {
        fetchRecurringPayments();
        fetchCategories();
    }, []);

    const fetchRecurringPayments = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/recurring-payments`);
            if (response.ok) {
                const data = await response.json();
                setRecurringPayments(data);
            }
        } catch (error) {
            console.error("Error fetching recurring payments:", error);
        }
    };

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

        const url = editingPayment
            ? `${import.meta.env.VITE_BACKEND_URL}/api/recurring-payments/${editingPayment.id}`
            : `${import.meta.env.VITE_BACKEND_URL}/api/recurring-payments`;

        const method = editingPayment ? 'PUT' : 'POST';

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                await fetchRecurringPayments();
                handleCloseModal();
            }
        } catch (error) {
            console.error("Error saving recurring payment:", error);
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('¿Estás seguro de que quieres eliminar este pago recurrente?')) {
            try {
                const response = await fetch(
                    `${import.meta.env.VITE_BACKEND_URL}/api/recurring-payments/${id}`,
                    { method: 'DELETE' }
                );

                if (response.ok) {
                    await fetchRecurringPayments();
                }
            } catch (error) {
                console.error("Error deleting recurring payment:", error);
            }
        }
    };

    const handleEdit = (payment) => {
        setEditingPayment(payment);
        setFormData({
            name: payment.name,
            amount: payment.amount.toString(),
            description: payment.description || '',
            frequency: payment.frequency,
            next_payment_date: payment.next_payment_date.split('T')[0],
            category_id: payment.category_id.toString(),
            is_active: payment.is_active
        });
        setShowModal(true);
    };

    const toggleActive = async (payment) => {
        try {
            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_URL}/api/recurring-payments/${payment.id}`,
                {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        ...payment,
                        is_active: !payment.is_active
                    }),
                }
            );

            if (response.ok) {
                await fetchRecurringPayments();
            }
        } catch (error) {
            console.error("Error toggling payment status:", error);
        }
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setEditingPayment(null);
        setFormData({
            name: '',
            amount: '',
            description: '',
            frequency: 'monthly',
            next_payment_date: new Date().toISOString().split('T')[0],
            category_id: '',
            is_active: true
        });
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 0
        }).format(amount);
    };

    const formatDate = (dateString) => {
        return format(new Date(dateString), 'dd MMM yyyy', { locale: es });
    };

    const getDaysUntilPayment = (paymentDate) => {
        const today = new Date();
        const payment = new Date(paymentDate);
        const diffTime = payment - today;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays;
    };

    const getFrequencyLabel = (frequency) => {
        const option = frequencyOptions.find(opt => opt.value === frequency);
        return option ? option.label : frequency;
    };

    const getUpcomingPayments = () => {
        return recurringPayments
            .filter(payment => payment.is_active)
            .sort((a, b) => new Date(a.next_payment_date) - new Date(b.next_payment_date))
            .slice(0, 5);
    };

    const getTotalMonthlyAmount = () => {
        return recurringPayments
            .filter(payment => payment.is_active)
            .reduce((total, payment) => {
                // Convertir a monto mensual basado en frecuencia
                let monthlyAmount = payment.amount;
                switch (payment.frequency) {
                    case 'daily':
                        monthlyAmount = payment.amount * 30;
                        break;
                    case 'weekly':
                        monthlyAmount = payment.amount * 4.33;
                        break;
                    case 'yearly':
                        monthlyAmount = payment.amount / 12;
                        break;
                    default: // monthly
                        monthlyAmount = payment.amount;
                }
                return total + monthlyAmount;
            }, 0);
    };

    const createDefaultRecurringPayments = async () => {
        const defaultPayments = [
            {
                name: 'Suscripción Netflix',
                amount: 15000,
                description: 'Entretenimiento mensual',
                frequency: 'monthly',
                next_payment_date: new Date(new Date().setDate(15)).toISOString().split('T')[0],
                category_id: categories.find(c => c.name.includes('Entretenimiento'))?.id || categories[0]?.id
            },
            {
                name: 'Servicio de Internet',
                amount: 80000,
                description: 'Internet de casa',
                frequency: 'monthly',
                next_payment_date: new Date(new Date().setDate(5)).toISOString().split('T')[0],
                category_id: categories.find(c => c.name.includes('Hogar'))?.id || categories[0]?.id
            },
            {
                name: 'Gimnasio',
                amount: 100000,
                description: 'Membresía mensual',
                frequency: 'monthly',
                next_payment_date: new Date(new Date().setDate(1)).toISOString().split('T')[0],
                category_id: categories.find(c => c.name.includes('Salud'))?.id || categories[0]?.id
            }
        ];

        for (const payment of defaultPayments) {
            if (payment.category_id) {
                try {
                    await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/recurring-payments`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(payment),
                    });
                } catch (error) {
                    console.error("Error creating default payment:", error);
                }
            }
        }

        await fetchRecurringPayments();
    };

    return (
        <div className="content-container fade-in">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h1>
                    <span>🔄</span>
                    Pagos Recurrentes
                </h1>
                <div className="d-flex gap-2">
                    {recurringPayments.length === 0 && categories.length > 0 && (
                        <button
                            className="btn btn-secondary"
                            onClick={createDefaultRecurringPayments}
                        >
                            <span>🎯</span>
                            Crear Ejemplos
                        </button>
                    )}
                    <button
                        className="btn btn-primary"
                        onClick={() => setShowModal(true)}
                    >
                        <span>➕</span>
                        Nuevo Pago Recurrente
                    </button>
                </div>
            </div>

            {/* Estadísticas */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon">🔄</div>
                    <span className="stat-value">
                        {recurringPayments.filter(p => p.is_active).length}
                    </span>
                    <div className="stat-label">Activos</div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">💸</div>
                    <span className="stat-value amount-expense">
                        {formatCurrency(getTotalMonthlyAmount())}
                    </span>
                    <div className="stat-label">Costo Mensual Estimado</div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">⏱️</div>
                    <span className="stat-value">
                        {getUpcomingPayments().length > 0
                            ? getDaysUntilPayment(getUpcomingPayments()[0].next_payment_date)
                            : '0'
                        }
                    </span>
                    <div className="stat-label">Días al Próximo Pago</div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">📊</div>
                    <span className="stat-value">
                        {recurringPayments.length}
                    </span>
                    <div className="stat-label">Total Configurados</div>
                </div>
            </div>

            <div className="row">
                {/* Próximos pagos */}
                <div className="col-md-6 mb-4">
                    <div className="card">
                        <div className="card-header">
                            <h4>⏰ Próximos Pagos</h4>
                        </div>
                        <div className="card-body p-0">
                            {getUpcomingPayments().length === 0 ? (
                                <div className="text-center p-4">
                                    <div style={{ fontSize: '3rem' }}>😴</div>
                                    <p>No hay pagos programados</p>
                                </div>
                            ) : (
                                <div className="transaction-list" style={{ maxHeight: '400px' }}>
                                    {getUpcomingPayments().map((payment) => {
                                        const daysUntil = getDaysUntilPayment(payment.next_payment_date);
                                        return (
                                            <div key={payment.id} className="transaction-item">
                                                <div className="transaction-info">
                                                    <div
                                                        className="transaction-icon"
                                                        style={{ backgroundColor: payment.category?.color || '#FF69B4' }}
                                                    >
                                                        {payment.category?.icon || '💰'}
                                                    </div>
                                                    <div className="transaction-details">
                                                        <h6>{payment.name}</h6>
                                                        <small>
                                                            {formatDate(payment.next_payment_date)}
                                                            {daysUntil === 0 && ' (¡Hoy!)'}
                                                            {daysUntil === 1 && ' (Mañana)'}
                                                            {daysUntil > 1 && ` (En ${daysUntil} días)`}
                                                            {daysUntil < 0 && ` (Vencido hace ${Math.abs(daysUntil)} días)`}
                                                        </small>
                                                    </div>
                                                </div>
                                                <div className="transaction-amount amount-expense">
                                                    {formatCurrency(payment.amount)}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Lista completa */}
                <div className="col-md-6 mb-4">
                    <div className="card">
                        <div className="card-header">
                            <h4>📋 Todos los Pagos</h4>
                        </div>
                        <div className="card-body p-0">
                            {recurringPayments.length === 0 ? (
                                <div className="text-center p-5">
                                    <div style={{ fontSize: '4rem' }}>😿</div>
                                    <h5>No hay pagos recurrentes</h5>
                                    <p>¡Configura tus suscripciones y membresías!</p>
                                </div>
                            ) : (
                                <div className="transaction-list">
                                    {recurringPayments.map((payment) => (
                                        <div key={payment.id} className="transaction-item">
                                            <div className="transaction-info">
                                                <div
                                                    className="transaction-icon"
                                                    style={{
                                                        backgroundColor: payment.category?.color || '#FF69B4',
                                                        opacity: payment.is_active ? 1 : 0.5
                                                    }}
                                                >
                                                    {payment.category?.icon || '💰'}
                                                </div>
                                                <div className="transaction-details">
                                                    <h6 style={{ opacity: payment.is_active ? 1 : 0.7 }}>
                                                        {payment.name}
                                                        {!payment.is_active && ' (Inactivo)'}
                                                    </h6>
                                                    <small>
                                                        {getFrequencyLabel(payment.frequency)} •
                                                        Próximo: {formatDate(payment.next_payment_date)}
                                                    </small>
                                                </div>
                                            </div>
                                            <div className="d-flex align-items-center gap-3">
                                                <div className="transaction-amount amount-expense">
                                                    {formatCurrency(payment.amount)}
                                                </div>
                                                <span className={`badge badge-${payment.is_active ? 'income' : 'expense'}`}>
                                                    {payment.is_active ? 'Activo' : 'Inactivo'}
                                                </span>
                                                <div className="d-flex gap-2">
                                                    <button
                                                        className={`btn btn-sm ${payment.is_active ? 'btn-danger' : 'btn-success'}`}
                                                        onClick={() => toggleActive(payment)}
                                                        title={payment.is_active ? 'Desactivar' : 'Activar'}
                                                    >
                                                        {payment.is_active ? '⏸️' : '▶️'}
                                                    </button>
                                                    <button
                                                        className="btn btn-sm btn-secondary"
                                                        onClick={() => handleEdit(payment)}
                                                    >
                                                        ✏️
                                                    </button>
                                                    <button
                                                        className="btn btn-sm btn-danger"
                                                        onClick={() => handleDelete(payment.id)}
                                                    >
                                                        🗑️
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Modal para agregar/editar pago recurrente */}
            {showModal && (
                <div className="modal-overlay" onClick={handleCloseModal}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h5>
                                {editingPayment ? '✏️ Editar Pago Recurrente' : '➕ Nuevo Pago Recurrente'}
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
                                        placeholder="Ej: Netflix, Gimnasio, Internet..."
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Monto</label>
                                    <input
                                        type="number"
                                        className="form-control"
                                        value={formData.amount}
                                        onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                                        placeholder="0"
                                        min="0"
                                        step="1"
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
                                    <label className="form-label">Frecuencia</label>
                                    <select
                                        className="form-control form-select"
                                        value={formData.frequency}
                                        onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
                                        required
                                    >
                                        {frequencyOptions.map(option => (
                                            <option key={option.value} value={option.value}>
                                                {option.label}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Categoría</label>
                                    <select
                                        className="form-control form-select"
                                        value={formData.category_id}
                                        onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                                        required
                                    >
                                        <option value="">Selecciona una categoría</option>
                                        {categories.map(category => (
                                            <option key={category.id} value={category.id}>
                                                {category.icon} {category.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Próximo Pago</label>
                                    <input
                                        type="date"
                                        className="form-control"
                                        value={formData.next_payment_date}
                                        onChange={(e) => setFormData({ ...formData, next_payment_date: e.target.value })}
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <div className="d-flex align-items-center gap-2">
                                        <input
                                            type="checkbox"
                                            id="is_active"
                                            checked={formData.is_active}
                                            onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                                        />
                                        <label htmlFor="is_active" className="form-label mb-0">
                                            Activo
                                        </label>
                                    </div>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" onClick={handleCloseModal}>
                                    Cancelar
                                </button>
                                <button type="submit" className="btn btn-primary">
                                    {editingPayment ? 'Actualizar' : 'Guardar'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RecurringPayments;
