import React, { useState, useEffect } from "react";
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const Transactions = () => {
    const [transactions, setTransactions] = useState([]);
    const [categories, setCategories] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [editingTransaction, setEditingTransaction] = useState(null);
    const [formData, setFormData] = useState({
        amount: '',
        description: '',
        transaction_type: 'expense',
        transaction_date: new Date().toISOString().split('T')[0],
        category_id: ''
    });
    const [filter, setFilter] = useState({
        type: 'all',
        month: new Date().getMonth() + 1,
        year: new Date().getFullYear()
    });

    useEffect(() => {
        fetchTransactions();
        fetchCategories();
    }, [filter]);

    const fetchTransactions = async () => {
        try {
            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_URL}/api/transactions?month=${filter.month}&year=${filter.year}`
            );
            if (response.ok) {
                const data = await response.json();
                setTransactions(data);
            }
        } catch (error) {
            console.error("Error fetching transactions:", error);
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

        const url = editingTransaction
            ? `${import.meta.env.VITE_BACKEND_URL}/api/transactions/${editingTransaction.id}`
            : `${import.meta.env.VITE_BACKEND_URL}/api/transactions`;

        const method = editingTransaction ? 'PUT' : 'POST';

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                await fetchTransactions();
                handleCloseModal();
            }
        } catch (error) {
            console.error("Error saving transaction:", error);
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('¿Estás seguro de que quieres eliminar esta transacción?')) {
            try {
                const response = await fetch(
                    `${import.meta.env.VITE_BACKEND_URL}/api/transactions/${id}`,
                    { method: 'DELETE' }
                );

                if (response.ok) {
                    await fetchTransactions();
                }
            } catch (error) {
                console.error("Error deleting transaction:", error);
            }
        }
    };

    const handleEdit = (transaction) => {
        setEditingTransaction(transaction);
        setFormData({
            amount: transaction.amount.toString(),
            description: transaction.description,
            transaction_type: transaction.transaction_type,
            transaction_date: transaction.transaction_date.split('T')[0],
            category_id: transaction.category_id.toString()
        });
        setShowModal(true);
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setEditingTransaction(null);
        setFormData({
            amount: '',
            description: '',
            transaction_type: 'expense',
            transaction_date: new Date().toISOString().split('T')[0],
            category_id: ''
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

    const filteredTransactions = transactions.filter(transaction => {
        if (filter.type === 'all') return true;
        return transaction.transaction_type === filter.type;
    });

    const totalIncome = transactions
        .filter(t => t.transaction_type === 'income')
        .reduce((sum, t) => sum + t.amount, 0);

    const totalExpenses = transactions
        .filter(t => t.transaction_type === 'expense')
        .reduce((sum, t) => sum + t.amount, 0);

    return (
        <div className="content-container fade-in">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h1>
                    <span>💰</span>
                    Transacciones
                </h1>
                <button
                    className="btn btn-primary"
                    onClick={() => setShowModal(true)}
                >
                    <span>➕</span>
                    Nueva Transacción
                </button>
            </div>

            {/* Resumen rápido */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon">💚</div>
                    <span className="stat-value amount-income">
                        {formatCurrency(totalIncome)}
                    </span>
                    <div className="stat-label">Total Ingresos</div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">💔</div>
                    <span className="stat-value amount-expense">
                        {formatCurrency(totalExpenses)}
                    </span>
                    <div className="stat-label">Total Gastos</div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">📊</div>
                    <span className={`stat-value ${(totalIncome - totalExpenses) >= 0 ? 'amount-income' : 'amount-expense'}`}>
                        {formatCurrency(totalIncome - totalExpenses)}
                    </span>
                    <div className="stat-label">Balance del Mes</div>
                </div>
            </div>

            {/* Filtros */}
            <div className="card mb-4">
                <div className="card-body">
                    <div className="row">
                        <div className="col-md-3">
                            <label className="form-label">Tipo</label>
                            <select
                                className="form-control form-select"
                                value={filter.type}
                                onChange={(e) => setFilter({ ...filter, type: e.target.value })}
                            >
                                <option value="all">Todos</option>
                                <option value="income">Ingresos</option>
                                <option value="expense">Gastos</option>
                            </select>
                        </div>
                        <div className="col-md-3">
                            <label className="form-label">Mes</label>
                            <select
                                className="form-control form-select"
                                value={filter.month}
                                onChange={(e) => setFilter({ ...filter, month: parseInt(e.target.value) })}
                            >
                                {Array.from({ length: 12 }, (_, i) => (
                                    <option key={i + 1} value={i + 1}>
                                        {new Date(2024, i).toLocaleDateString('es-CO', { month: 'long' })}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div className="col-md-3">
                            <label className="form-label">Año</label>
                            <select
                                className="form-control form-select"
                                value={filter.year}
                                onChange={(e) => setFilter({ ...filter, year: parseInt(e.target.value) })}
                            >
                                {Array.from({ length: 5 }, (_, i) => (
                                    <option key={2024 - i} value={2024 - i}>
                                        {2024 - i}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            {/* Lista de transacciones */}
            <div className="card">
                <div className="card-header">
                    <h4>
                        📋 Lista de Transacciones
                        {filteredTransactions.length > 0 && (
                            <span className="badge badge-recurring ms-2">
                                {filteredTransactions.length} transacciones
                            </span>
                        )}
                    </h4>
                </div>
                <div className="card-body p-0">
                    {filteredTransactions.length === 0 ? (
                        <div className="text-center p-5">
                            <div style={{ fontSize: '4rem' }}>😿</div>
                            <h5>No hay transacciones registradas</h5>
                            <p>¡Comienza agregando tu primera transacción!</p>
                        </div>
                    ) : (
                        <div className="transaction-list">
                            {filteredTransactions.map((transaction) => (
                                <div key={transaction.id} className="transaction-item">
                                    <div className="transaction-info">
                                        <div
                                            className="transaction-icon"
                                            style={{ backgroundColor: transaction.category?.color || '#FF69B4' }}
                                        >
                                            {transaction.category?.icon || '💰'}
                                        </div>
                                        <div className="transaction-details">
                                            <h6>{transaction.description}</h6>
                                            <small>
                                                {transaction.category?.name} • {formatDate(transaction.transaction_date)}
                                            </small>
                                        </div>
                                    </div>
                                    <div className="d-flex align-items-center gap-3">
                                        <div className={`transaction-amount ${transaction.transaction_type === 'income' ? 'amount-income' : 'amount-expense'}`}>
                                            {transaction.transaction_type === 'income' ? '+' : '-'}
                                            {formatCurrency(transaction.amount)}
                                        </div>
                                        <span className={`badge badge-${transaction.transaction_type === 'income' ? 'income' : 'expense'}`}>
                                            {transaction.transaction_type === 'income' ? 'Ingreso' : 'Gasto'}
                                        </span>
                                        <div className="d-flex gap-2">
                                            <button
                                                className="btn btn-sm btn-secondary"
                                                onClick={() => handleEdit(transaction)}
                                            >
                                                ✏️
                                            </button>
                                            <button
                                                className="btn btn-sm btn-danger"
                                                onClick={() => handleDelete(transaction.id)}
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

            {/* Modal para agregar/editar transacción */}
            {showModal && (
                <div className="modal-overlay" onClick={handleCloseModal}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h5>
                                {editingTransaction ? '✏️ Editar Transacción' : '➕ Nueva Transacción'}
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
                                    <label className="form-label">Tipo de Transacción</label>
                                    <select
                                        className="form-control form-select"
                                        value={formData.transaction_type}
                                        onChange={(e) => setFormData({ ...formData, transaction_type: e.target.value })}
                                        required
                                    >
                                        <option value="expense">💸 Gasto</option>
                                        <option value="income">💰 Ingreso</option>
                                    </select>
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
                                    <input
                                        type="text"
                                        className="form-control"
                                        value={formData.description}
                                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                        placeholder="Describe tu transacción..."
                                        required
                                    />
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
                                    <label className="form-label">Fecha</label>
                                    <input
                                        type="date"
                                        className="form-control"
                                        value={formData.transaction_date}
                                        onChange={(e) => setFormData({ ...formData, transaction_date: e.target.value })}
                                        required
                                    />
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" onClick={handleCloseModal}>
                                    Cancelar
                                </button>
                                <button type="submit" className="btn btn-primary">
                                    {editingTransaction ? 'Actualizar' : 'Guardar'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Transactions;
