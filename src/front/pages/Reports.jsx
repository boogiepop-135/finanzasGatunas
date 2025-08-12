import React, { useState, useEffect } from "react";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, AreaChart, Area } from 'recharts';

const Reports = () => {
    const [summary, setSummary] = useState({
        income: 0,
        expenses: 0,
        balance: 0,
        expenses_by_category: []
    });
    const [monthlyTrend, setMonthlyTrend] = useState([]);
    const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
    const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
    const [reportType, setReportType] = useState('monthly');

    const CHART_COLORS = ['#FF69B4', '#FFB6C1', '#DDA0DD', '#F0E68C', '#98FB98', '#87CEEB', '#FFA07A', '#FFE4E1'];

    useEffect(() => {
        fetchDashboardData();
        fetchMonthlyTrend();
    }, [selectedMonth, selectedYear, reportType]);

    const fetchDashboardData = async () => {
        try {
            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_URL}/api/dashboard/summary?month=${selectedMonth}&year=${selectedYear}`
            );
            if (response.ok) {
                const data = await response.json();
                setSummary(data);
            }
        } catch (error) {
            console.error("Error fetching dashboard data:", error);
        }
    };

    const fetchMonthlyTrend = async () => {
        try {
            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_URL}/api/dashboard/monthly-trend?year=${selectedYear}`
            );
            if (response.ok) {
                const data = await response.json();
                setMonthlyTrend(data);
            }
        } catch (error) {
            console.error("Error fetching monthly trend:", error);
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
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ];
        return months[monthNumber - 1];
    };

    const formatMonthlyData = monthlyTrend.map((item, index) => ({
        ...item,
        month: getMonthName(item.month),
        monthShort: getMonthName(item.month).substring(0, 3),
        savings: item.income - item.expenses,
        savingsPercentage: item.income > 0 ? ((item.income - item.expenses) / item.income * 100) : 0
    }));

    const calculateYearlyTotals = () => {
        const totals = monthlyTrend.reduce((acc, month) => ({
            income: acc.income + month.income,
            expenses: acc.expenses + month.expenses,
            balance: acc.balance + month.balance
        }), { income: 0, expenses: 0, balance: 0 });

        return {
            ...totals,
            savingsRate: totals.income > 0 ? ((totals.income - totals.expenses) / totals.income * 100) : 0,
            averageMonthlyIncome: totals.income / 12,
            averageMonthlyExpenses: totals.expenses / 12
        };
    };

    const getTopExpenseCategories = () => {
        return summary.expenses_by_category
            .sort((a, b) => b.amount - a.amount)
            .slice(0, 5);
    };

    const getBestSavingsMonths = () => {
        return formatMonthlyData
            .filter(month => month.savings > 0)
            .sort((a, b) => b.savings - a.savings)
            .slice(0, 3);
    };

    const getWorstExpenseMonths = () => {
        return formatMonthlyData
            .sort((a, b) => b.expenses - a.expenses)
            .slice(0, 3);
    };

    const yearlyTotals = calculateYearlyTotals();

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <div className="card p-3 shadow-medium">
                    <p className="mb-2"><strong>{label}</strong></p>
                    {payload.map((entry, index) => (
                        <p key={index} style={{ color: entry.color }} className="mb-1">
                            {entry.name}: {formatCurrency(entry.value)}
                        </p>
                    ))}
                </div>
            );
        }
        return null;
    };

    return (
        <div className="content-container fade-in">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h1>
                    <span>📊</span>
                    Reportes Financieros
                </h1>

                {/* Filtros */}
                <div className="d-flex gap-3">
                    <select
                        className="form-control form-select"
                        value={reportType}
                        onChange={(e) => setReportType(e.target.value)}
                        style={{ width: 'auto' }}
                    >
                        <option value="monthly">📅 Reporte Mensual</option>
                        <option value="yearly">📋 Reporte Anual</option>
                    </select>

                    {reportType === 'monthly' && (
                        <select
                            className="form-control form-select"
                            value={selectedMonth}
                            onChange={(e) => setSelectedMonth(parseInt(e.target.value))}
                            style={{ width: 'auto' }}
                        >
                            {Array.from({ length: 12 }, (_, i) => (
                                <option key={i + 1} value={i + 1}>
                                    {getMonthName(i + 1)}
                                </option>
                            ))}
                        </select>
                    )}

                    <select
                        className="form-control form-select"
                        value={selectedYear}
                        onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                        style={{ width: 'auto' }}
                    >
                        {Array.from({ length: 5 }, (_, i) => (
                            <option key={2024 - i} value={2024 - i}>
                                {2024 - i}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Resumen Ejecutivo */}
            <div className="card mb-4">
                <div className="card-header">
                    <h4>📈 Resumen Ejecutivo - {reportType === 'monthly' ? `${getMonthName(selectedMonth)} ${selectedYear}` : selectedYear}</h4>
                </div>
                <div className="card-body">
                    <div className="stats-grid">
                        <div className="stat-card">
                            <div className="stat-icon">💰</div>
                            <span className="stat-value amount-income">
                                {formatCurrency(reportType === 'monthly' ? summary.income : yearlyTotals.income)}
                            </span>
                            <div className="stat-label">
                                {reportType === 'monthly' ? 'Ingresos del Mes' : 'Ingresos del Año'}
                            </div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-icon">💸</div>
                            <span className="stat-value amount-expense">
                                {formatCurrency(reportType === 'monthly' ? summary.expenses : yearlyTotals.expenses)}
                            </span>
                            <div className="stat-label">
                                {reportType === 'monthly' ? 'Gastos del Mes' : 'Gastos del Año'}
                            </div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-icon">🏦</div>
                            <span className={`stat-value ${(reportType === 'monthly' ? summary.balance : yearlyTotals.balance) >= 0 ? 'amount-income' : 'amount-expense'}`}>
                                {formatCurrency(reportType === 'monthly' ? summary.balance : yearlyTotals.balance)}
                            </span>
                            <div className="stat-label">Balance</div>
                        </div>

                        {reportType === 'yearly' && (
                            <div className="stat-card">
                                <div className="stat-icon">📊</div>
                                <span className={`stat-value ${yearlyTotals.savingsRate >= 0 ? 'amount-income' : 'amount-expense'}`}>
                                    {yearlyTotals.savingsRate.toFixed(1)}%
                                </span>
                                <div className="stat-label">Tasa de Ahorro</div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {reportType === 'yearly' && (
                <>
                    {/* Tendencia Anual */}
                    <div className="row mb-4">
                        <div className="col-12">
                            <div className="chart-container">
                                <h3 className="chart-title">
                                    📈 Tendencia Financiera {selectedYear}
                                </h3>
                                <ResponsiveContainer width="100%" height={400}>
                                    <AreaChart data={formatMonthlyData}>
                                        <defs>
                                            <linearGradient id="colorIncome" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#98FB98" stopOpacity={0.8} />
                                                <stop offset="95%" stopColor="#98FB98" stopOpacity={0.1} />
                                            </linearGradient>
                                            <linearGradient id="colorExpenses" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#FF6B6B" stopOpacity={0.8} />
                                                <stop offset="95%" stopColor="#FF6B6B" stopOpacity={0.1} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="monthShort" />
                                        <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`} />
                                        <Tooltip content={<CustomTooltip />} />
                                        <Area
                                            type="monotone"
                                            dataKey="income"
                                            stroke="#98FB98"
                                            fillOpacity={1}
                                            fill="url(#colorIncome)"
                                            name="Ingresos"
                                        />
                                        <Area
                                            type="monotone"
                                            dataKey="expenses"
                                            stroke="#FF6B6B"
                                            fillOpacity={1}
                                            fill="url(#colorExpenses)"
                                            name="Gastos"
                                        />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>

                    {/* Análisis de Ahorros */}
                    <div className="row mb-4">
                        <div className="col-md-8">
                            <div className="chart-container">
                                <h3 className="chart-title">
                                    💰 Evolución de Ahorros {selectedYear}
                                </h3>
                                <ResponsiveContainer width="100%" height={300}>
                                    <BarChart data={formatMonthlyData}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="monthShort" />
                                        <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`} />
                                        <Tooltip content={<CustomTooltip />} />
                                        <Bar
                                            dataKey="savings"
                                            fill="#FF69B4"
                                            name="Ahorros"
                                        />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        <div className="col-md-4">
                            <div className="card h-100">
                                <div className="card-header">
                                    <h5>🏆 Mejores Meses para Ahorrar</h5>
                                </div>
                                <div className="card-body">
                                    {getBestSavingsMonths().length === 0 ? (
                                        <div className="text-center">
                                            <div style={{ fontSize: '2rem' }}>😿</div>
                                            <p>No hay meses con ahorros positivos</p>
                                        </div>
                                    ) : (
                                        getBestSavingsMonths().map((month, index) => (
                                            <div key={month.month} className="d-flex justify-content-between align-items-center mb-3">
                                                <div>
                                                    <span className="badge badge-income">#{index + 1}</span>
                                                    <strong className="ms-2">{month.month}</strong>
                                                </div>
                                                <span className="amount-income">
                                                    {formatCurrency(month.savings)}
                                                </span>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            )}

            {/* Gastos por Categoría */}
            <div className="row mb-4">
                <div className="col-md-8">
                    <div className="chart-container">
                        <h3 className="chart-title">
                            🍕 Distribución de Gastos por Categoría
                        </h3>
                        {summary.expenses_by_category.length > 0 ? (
                            <ResponsiveContainer width="100%" height={350}>
                                <PieChart>
                                    <Pie
                                        data={summary.expenses_by_category}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={false}
                                        label={({ name, value, percent }) =>
                                            `${name}: ${(percent * 100).toFixed(1)}%`
                                        }
                                        outerRadius={120}
                                        fill="#8884d8"
                                        dataKey="amount"
                                    >
                                        {summary.expenses_by_category.map((entry, index) => (
                                            <Cell
                                                key={`cell-${index}`}
                                                fill={entry.color || CHART_COLORS[index % CHART_COLORS.length]}
                                            />
                                        ))}
                                    </Pie>
                                    <Tooltip content={<CustomTooltip />} />
                                </PieChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="text-center p-5">
                                <div style={{ fontSize: '4rem' }}>😴</div>
                                <p>No hay datos de gastos para mostrar</p>
                            </div>
                        )}
                    </div>
                </div>

                <div className="col-md-4">
                    <div className="card h-100">
                        <div className="card-header">
                            <h5>🔥 Top Categorías de Gasto</h5>
                        </div>
                        <div className="card-body">
                            {getTopExpenseCategories().length === 0 ? (
                                <div className="text-center">
                                    <div style={{ fontSize: '2rem' }}>😴</div>
                                    <p>No hay gastos registrados</p>
                                </div>
                            ) : (
                                getTopExpenseCategories().map((category, index) => (
                                    <div key={category.name} className="d-flex justify-content-between align-items-center mb-3">
                                        <div className="d-flex align-items-center gap-2">
                                            <span className="badge badge-expense">#{index + 1}</span>
                                            <div
                                                style={{
                                                    width: '20px',
                                                    height: '20px',
                                                    backgroundColor: category.color,
                                                    borderRadius: '50%',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    fontSize: '0.8rem'
                                                }}
                                            >
                                                {category.icon}
                                            </div>
                                            <strong>{category.name}</strong>
                                        </div>
                                        <span className="amount-expense">
                                            {formatCurrency(category.amount)}
                                        </span>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {reportType === 'yearly' && (
                /* Insights y Recomendaciones */
                <div className="row">
                    <div className="col-md-6">
                        <div className="card">
                            <div className="card-header">
                                <h5>💡 Insights Financieros</h5>
                            </div>
                            <div className="card-body">
                                <div className="mb-3">
                                    <strong>📊 Promedio Mensual:</strong>
                                    <div className="ms-3">
                                        <div>💰 Ingresos: {formatCurrency(yearlyTotals.averageMonthlyIncome)}</div>
                                        <div>💸 Gastos: {formatCurrency(yearlyTotals.averageMonthlyExpenses)}</div>
                                    </div>
                                </div>

                                <div className="mb-3">
                                    <strong>🎯 Tasa de Ahorro:</strong>
                                    <div className="ms-3">
                                        <span className={yearlyTotals.savingsRate >= 20 ? 'amount-income' : yearlyTotals.savingsRate >= 10 ? 'text-warning' : 'amount-expense'}>
                                            {yearlyTotals.savingsRate.toFixed(1)}%
                                        </span>
                                        {yearlyTotals.savingsRate >= 20 && <span className="ms-2">🎉 ¡Excelente!</span>}
                                        {yearlyTotals.savingsRate >= 10 && yearlyTotals.savingsRate < 20 && <span className="ms-2">👍 Bien</span>}
                                        {yearlyTotals.savingsRate < 10 && <span className="ms-2">⚠️ Mejorable</span>}
                                    </div>
                                </div>

                                <div className="mb-3">
                                    <strong>📈 Mejor Mes:</strong>
                                    <div className="ms-3">
                                        {getBestSavingsMonths()[0] ? (
                                            <span>
                                                {getBestSavingsMonths()[0].month} - {formatCurrency(getBestSavingsMonths()[0].savings)}
                                            </span>
                                        ) : (
                                            <span>No hay datos suficientes</span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="col-md-6">
                        <div className="card">
                            <div className="card-header">
                                <h5>🐱 Consejos Gatunos</h5>
                            </div>
                            <div className="card-body">
                                {yearlyTotals.savingsRate < 10 ? (
                                    <div className="alert alert-info">
                                        <div style={{ fontSize: '2rem' }}>😾</div>
                                        <strong>¡Necesitas mejorar tus ahorros!</strong>
                                        <ul className="mt-2 mb-0">
                                            <li>Revisa tus gastos principales</li>
                                            <li>Establece un presupuesto mensual</li>
                                            <li>Considera reducir gastos no esenciales</li>
                                        </ul>
                                    </div>
                                ) : yearlyTotals.savingsRate < 20 ? (
                                    <div className="alert alert-success">
                                        <div style={{ fontSize: '2rem' }}>😸</div>
                                        <strong>¡Vas por buen camino!</strong>
                                        <ul className="mt-2 mb-0">
                                            <li>Intenta aumentar tu tasa de ahorro al 20%</li>
                                            <li>Considera invertir tus ahorros</li>
                                            <li>Mantén el control de gastos</li>
                                        </ul>
                                    </div>
                                ) : (
                                    <div className="alert alert-success">
                                        <div style={{ fontSize: '2rem' }}>😻</div>
                                        <strong>¡Eres un genio financiero!</strong>
                                        <ul className="mt-2 mb-0">
                                            <li>Considera diversificar inversiones</li>
                                            <li>Piensa en metas financieras a largo plazo</li>
                                            <li>¡Sigue así!</li>
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Reports;
