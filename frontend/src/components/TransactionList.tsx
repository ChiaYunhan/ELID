import { useEffect, useState } from "react";
import type { Transaction } from "../types/index";
import { apiClient } from "../api/client";

export function TransactionList() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchTransactions = async () => {
    try {
      const data = await apiClient.getTransactions(50, 0);
      setTransactions(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load transactions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();

    if (autoRefresh) {
      const interval = setInterval(fetchTransactions, 3000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  if (loading) {
    return <div className="loading">Loading transactions...</div>;
  }

  return (
    <div className="transaction-list">
      <div className="transaction-header">
        <h2>Recent Transactions ({transactions.length})</h2>
        <label className="auto-refresh-toggle">
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
          />
          Auto-refresh
        </label>
      </div>

      {error && <div className="error-message">{error}</div>}

      {transactions.length === 0 ? (
        <div className="empty-state">
          No transactions yet. Activate a device to start generating transactions.
        </div>
      ) : (
        <div className="transactions-table-container">
          <table className="transactions-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Device ID</th>
                <th>Username</th>
                <th>Event Type</th>
                <th>Payload</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((transaction) => (
                <tr key={transaction.transaction_id}>
                  <td className="timestamp">
                    {formatTimestamp(transaction.timestamp)}
                  </td>
                  <td className="device-id">{transaction.device_id.slice(0, 8)}...</td>
                  <td>{transaction.username}</td>
                  <td>
                    <span className={`event-badge ${transaction.event_type}`}>
                      {transaction.event_type}
                    </span>
                  </td>
                  <td className="payload">
                    {JSON.stringify(transaction.payload)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
