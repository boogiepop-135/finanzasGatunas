import React, { useState, useEffect } from "react";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import useGlobalReducer from "../hooks/useGlobalReducer";

const Dashboard = () => {
    const { store } = useGlobalReducer();
    const backendUrl = store.backendUrl || '/api';

    const [summary, setSummary] = useState({
        income: 0,
        expenses: 0,
        balance: 0,
        expenses_by_category: []
    });
    const [monthlyTrend, setMonthlyTrend] = useState([]);
    const [currentMonth] = useState(new Date().getMonth() + 1);
    const [currentYear] = useState(new Date().getFullYear());

    const CHART_COLORS = ['#FF69B4', '#FFB6C1', '#DDA0DD', '#F0E68C', '#98FB98', '#87CEEB'];

    useEffect(() => {
        console.log("Dashboard montado, backend URL:", backendUrl);
        fetchDashboardData();
        fetchMonthlyTrend();
    }, []);

    const fetchDashboardData = async () => {
        try {
            console.log("Intentando fetch a:", `${backendUrl}/dashboard/summary?month=${currentMonth}&year=${currentYear}`);
            const response = await fetch(`${backendUrl}/dashboard/summary?month=${currentMonth}&year=${currentYear}`);
            if (response.ok) {
                const data = await response.json();
                setSummary(data);
            } else {
                console.warn("Error en la respuesta del servidor:", response.status);
            }
        } catch (error) {
            console.error("Error fetching dashboard data:", error);
            // Establecer datos de ejemplo en caso de error
            setSummary({
                income: 5000,
                expenses: 3000,
                balance: 2000,
                expenses_by_category: [
                    { name: 'Alimentación', value: 1000 },
                    { name: 'Transporte', value: 800 },
                    { name: 'Entretenimiento', value: 600 },
                    { name: 'Otros', value: 600 }
                ]
            });
        }
    };

    const fetchMonthlyTrend = async () => {
        try {
            const response = await fetch(`${backendUrl}/dashboard/monthly-trend?year=${currentYear}`);
            if (response.ok) {
                const data = await response.json();
                setMonthlyTrend(data);
            } else {
                console.warn("Error en la respuesta del servidor para trend:", response.status);
            }
        } catch (error) {
            console.error("Error fetching monthly trend:", error);
            // Establecer datos de ejemplo en caso de error
            setMonthlyTrend([
                { month: 'Ene', income: 4500, expenses: 3200 },
                { month: 'Feb', income: 4800, expenses: 3100 },
                { month: 'Mar', income: 5000, expenses: 3000 },
                { month: 'Abr', income: 4700, expenses: 3300 },
                { month: 'May', income: 5200, expenses: 2900 },
                { month: 'Jun', income: 4900, expenses: 3100 }
            ]);
        }
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 0
        }).format(amount);
    };

    const getMonthName = (monthNumber) => {
        const months = [
            'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
            'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
        ];
        return months[monthNumber - 1];
    };

    const formatMonthlyData = monthlyTrend.map(item => ({
        ...item,
        month: getMonthName(item.month)
    }));

    return (
        <div className="content-container fade-in">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h1 className="text-center">
                    <span className="cat-emoji">🐱</span>
                    Dashboard Financiero Gatuno
                </h1>
                <div className="text-right">
                    <small>
                        📅 {new Date().toLocaleDateString('es-CO', {
                            year: 'numeric',
                            month: 'long'
                        })}
                    </small>
                </div>
            </div>

            {/* Resumen de estadísticas */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon">💰</div>
                    <span className="stat-value amount-income">
                        {formatCurrency(summary.income)}
                    </span>
                    <div className="stat-label">Ingresos del Mes</div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">💸</div>
                    <span className="stat-value amount-expense">
                        {formatCurrency(summary.expenses)}
                    </span>
                    <div className="stat-label">Gastos del Mes</div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">🏦</div>
                    <span className={`stat-value ${summary.balance >= 0 ? 'amount-income' : 'amount-expense'}`}>
                        {formatCurrency(summary.balance)}
                    </span>
                    <div className="stat-label">Balance</div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">😸</div>
                    <span className="stat-value">
                        {summary.balance >= 0 ? '😸' : '😿'}
                    </span>
                    <div className="stat-label">Estado Gatuno</div>
                </div>
            </div>

            <div className="row">
                {/* Gráfico de gastos por categoría */}
                <div className="col-md-6 mb-4">
                    <div className="chart-container">
                        <h3 className="chart-title">
                            🍕 Gastos por Categoría
                        </h3>
                        {summary.expenses_by_category.length > 0 ? (
                            <ResponsiveContainer width="100%" height={300}>
                                <PieChart>
                                    <Pie
                                        data={summary.expenses_by_category}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={false}
                                        label={({ name, value }) => `${name}: ${formatCurrency(value)}`}
                                        outerRadius={80}
                                        fill="#8884d8"
                                        dataKey="amount"
                                    >
                                        {summary.expenses_by_category.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color || CHART_COLORS[index % CHART_COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip formatter={(value) => formatCurrency(value)} />
                                </PieChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="text-center p-4">
                                <div style={{ fontSize: '4rem' }}>😴</div>
                                <p>No hay gastos registrados este mes</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Tendencia mensual */}
                <div className="col-md-6 mb-4">
                    <div className="chart-container">
                        <h3 className="chart-title">
                            📈 Tendencia Mensual {currentYear}
                        </h3>
                        {formatMonthlyData.length > 0 ? (
                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={formatMonthlyData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="month" />
                                    <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`} />
                                    <Tooltip formatter={(value) => formatCurrency(value)} />
                                    <Line
                                        type="monotone"
                                        dataKey="income"
                                        stroke="#98FB98"
                                        strokeWidth={3}
                                        name="Ingresos"
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="expenses"
                                        stroke="#FF6B6B"
                                        strokeWidth={3}
                                        name="Gastos"
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="balance"
                                        stroke="#FF69B4"
                                        strokeWidth={3}
                                        name="Balance"
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="text-center p-4">
                                <div style={{ fontSize: '4rem' }}>📊</div>
                                <p>Cargando datos de tendencia...</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Comparación anual */}
            <div className="row">
                <div className="col-12">
                    <div className="chart-container">
                        <h3 className="chart-title">
                            📊 Comparación Ingresos vs Gastos {currentYear}
                        </h3>
                        {formatMonthlyData.length > 0 ? (
                            <ResponsiveContainer width="100%" height={350}>
                                <BarChart data={formatMonthlyData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="month" />
                                    <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`} />
                                    <Tooltip formatter={(value) => formatCurrency(value)} />
                                    <Bar dataKey="income" fill="#98FB98" name="Ingresos" />
                                    <Bar dataKey="expenses" fill="#FF6B6B" name="Gastos" />
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="text-center p-4">
                                <div style={{ fontSize: '4rem' }}>📊</div>
                                <p>Cargando comparación anual...</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Consejos gatunos */}
            <div className="card mt-4">
                <div className="card-header">
                    <h4>💡 Consejos Financieros Gatunos</h4>
                </div>
                <div className="card-body">
                    <div className="row">
                        <div className="col-md-4 text-center mb-3">
                            <div style={{ fontSize: '3rem' }}>😸</div>
                            <h6>Mantén un presupuesto</h6>
                            <p>Como un gato organizado, controla tus gastos diarios</p>
                        </div>
                        <div className="col-md-4 text-center mb-3">
                            <div style={{ fontSize: '3rem' }}>💰</div>
                            <h6>Ahorra consistentemente</h6>
                            <p>Guarda una parte de tus ingresos como si fuera tu comida favorita</p>
                        </div>
                        <div className="col-md-4 text-center mb-3">
                            <div style={{ fontSize: '3rem' }}>📊</div>
                            <h6>Revisa tus gastos</h6>
                            <p>Analiza tus hábitos financieros regularmente</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
