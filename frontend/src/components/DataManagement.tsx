import { useState } from 'react';
import { api } from '../services/api';
import type { ExportData, ImportPreview, ImportResult } from '../types';
import './DataManagement.css';

export function DataManagement() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Export state
  const [includeSensorReadings, setIncludeSensorReadings] = useState(false);

  // Import state
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importMode, setImportMode] = useState<'dry_run' | 'merge' | 'overwrite'>('dry_run');
  const [preview, setPreview] = useState<ImportPreview | null>(null);
  const [importData, setImportData] = useState<ExportData | null>(null);
  const [importResult, setImportResult] = useState<ImportResult | null>(null);

  const handleExport = async () => {
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const data = await api.exportData(includeSensorReadings);

      // Create blob and download
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;

      // Create filename with timestamp
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      a.download = `gardening-data-export-${timestamp}.json`;

      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      setSuccess('Data exported successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export data');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setImportFile(file);
    setPreview(null);
    setImportResult(null);
    setError('');
    setSuccess('');

    try {
      const text = await file.text();
      const data: ExportData = JSON.parse(text);
      setImportData(data);

      // Auto-preview after file selection
      await handlePreview(data);
    } catch (err) {
      setError('Invalid JSON file. Please select a valid export file.');
      setImportFile(null);
      setImportData(null);
    }
  };

  const handlePreview = async (data: ExportData) => {
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const previewResult = await api.previewImport(data, importMode);
      setPreview(previewResult);

      if (!previewResult.valid) {
        setError('Import validation failed. See issues below.');
      } else if (previewResult.issues.length > 0) {
        setSuccess('Import is valid but has warnings. Review before proceeding.');
      } else {
        setSuccess('Import validation passed!');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to validate import');
      setPreview(null);
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    if (!importData || !preview) return;

    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await api.importData({
        mode: importMode,
        data: importData
      });

      setImportResult(result);

      if (result.success) {
        if (importMode === 'dry_run') {
          setSuccess('Dry run completed successfully. No changes were made.');
        } else {
          setSuccess(`Import completed successfully! Imported ${Object.values(result.items_imported).reduce((a, b) => a + b, 0)} items.`);
          // Reload page after successful import to refresh data
          setTimeout(() => {
            window.location.reload();
          }, 2000);
        }
      } else {
        setError('Import failed: ' + result.errors.join(', '));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to import data');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityClass = (severity: string) => {
    switch (severity) {
      case 'error':
        return 'severity-error';
      case 'warning':
        return 'severity-warning';
      case 'info':
        return 'severity-info';
      default:
        return '';
    }
  };

  return (
    <div className="data-management">
      <h3>Data Management</h3>
      <p className="description">
        Export your data to a portable JSON file for backup or transfer.
        Import data from a previous export to restore or migrate your gardening information.
      </p>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      {/* Export Section */}
      <div className="section export-section">
        <h4>Export Data</h4>
        <p>Download all your gardening data as a JSON file.</p>

        <div className="form-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={includeSensorReadings}
              onChange={(e) => setIncludeSensorReadings(e.target.checked)}
              disabled={loading}
            />
            Include sensor readings (may create large file)
          </label>
        </div>

        <button
          onClick={handleExport}
          disabled={loading}
          className="btn btn-primary"
        >
          {loading ? 'Exporting...' : 'Download Export File'}
        </button>

        <div className="help-text">
          <strong>What's included:</strong> User profile (non-sensitive), lands, gardens,
          trees, plantings, soil samples, irrigation data, and optionally sensor readings.
          <br />
          <strong>Not included:</strong> Email, password, and authentication tokens.
        </div>
      </div>

      {/* Import Section */}
      <div className="section import-section">
        <h4>Import Data</h4>
        <p>Upload a JSON export file to import data.</p>

        <div className="form-group">
          <label>Select Export File</label>
          <input
            type="file"
            accept=".json"
            onChange={handleFileSelect}
            disabled={loading}
          />
        </div>

        {importFile && (
          <>
            <div className="form-group">
              <label>Import Mode</label>
              <select
                value={importMode}
                onChange={(e) => {
                  setImportMode(e.target.value as 'dry_run' | 'merge' | 'overwrite');
                  // Re-preview with new mode
                  if (importData) {
                    handlePreview(importData);
                  }
                }}
                disabled={loading}
              >
                <option value="dry_run">Dry Run (validate only, make no changes)</option>
                <option value="merge">Merge (add imported data to existing)</option>
                <option value="overwrite">Overwrite (delete all existing data first) ⚠️</option>
              </select>
            </div>

            <div className="mode-description">
              {importMode === 'dry_run' && (
                <p>
                  <strong>Dry Run:</strong> Validates the import file without making any changes.
                  Use this to check for errors before importing.
                </p>
              )}
              {importMode === 'merge' && (
                <p>
                  <strong>Merge:</strong> Imports data alongside your existing data.
                  New IDs will be assigned while preserving relationships.
                </p>
              )}
              {importMode === 'overwrite' && (
                <p className="warning">
                  <strong>⚠️ Overwrite:</strong> DELETES all your existing data before importing.
                  This is destructive and cannot be undone. Export your current data first!
                </p>
              )}
            </div>

            {preview && (
              <div className="preview-results">
                <h5>Validation Results</h5>

                <div className="preview-summary">
                  <div className={`schema-compat ${preview.schema_version_compatible ? 'compatible' : 'incompatible'}`}>
                    Schema Version: {preview.schema_version_compatible ? '✓ Compatible' : '✗ Incompatible'}
                  </div>
                  <div className={`validity ${preview.valid ? 'valid' : 'invalid'}`}>
                    {preview.valid ? '✓ Valid' : '✗ Invalid'}
                  </div>
                </div>

                <div className="import-counts">
                  <h6>Items to Import:</h6>
                  <ul>
                    {Object.entries(preview.counts).map(([key, count]) => (
                      <li key={key}>{key}: {count}</li>
                    ))}
                  </ul>
                </div>

                {importMode === 'overwrite' && preview.would_overwrite !== undefined && (
                  <div className="warning-box">
                    ⚠️ Overwrite mode will delete {preview.would_overwrite} existing items
                  </div>
                )}

                {preview.issues.length > 0 && (
                  <div className="issues-list">
                    <h6>Validation Issues:</h6>
                    {preview.issues.map((issue, index) => (
                      <div key={index} className={`issue ${getSeverityClass(issue.severity)}`}>
                        <div className="issue-header">
                          <span className="severity">{issue.severity.toUpperCase()}</span>
                          <span className="category">{issue.category}</span>
                        </div>
                        <div className="message">{issue.message}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {preview && (
              <div className="import-actions">
                <button
                  onClick={handleImport}
                  disabled={loading || !preview.valid}
                  className={importMode === 'overwrite' ? 'btn btn-danger' : 'btn btn-primary'}
                >
                  {loading ? 'Processing...' :
                   importMode === 'dry_run' ? 'Run Validation' :
                   importMode === 'overwrite' ? '⚠️ Overwrite All Data' :
                   'Import Data'}
                </button>
              </div>
            )}

            {importResult && importResult.success && importMode !== 'dry_run' && (
              <div className="import-result">
                <h5>Import Summary</h5>
                <div className="result-counts">
                  <h6>Items Imported:</h6>
                  <ul>
                    {Object.entries(importResult.items_imported).map(([key, count]) => (
                      <li key={key}>{key}: {count}</li>
                    ))}
                  </ul>
                </div>
                {importMode === 'overwrite' && importResult.items_deleted && (
                  <div className="warning-box">
                    Deleted {importResult.items_deleted} existing items
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
