// frontend/src/App.jsx - V2.2 + export CSV
// L'operatore preme il pulsante per dire "HO FATTO LA CADUTA"
// Aggiunto: pulsanti di download CSV in fondo

import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

export default function App() {
  // ==================== STATE - FORM ====================
  const [corda, setCorda] = useState('')
  const [assicuratore, setAssicuratore] = useState('')
  const [operatore, setOperatore] = useState('')
  
  // ==================== STATE - PRESETS ====================
  const [presets, setPresets] = useState([])
  const [selectedPreset, setSelectedPreset] = useState('')
  const [nuovoNomePreset, setNuovoNomePreset] = useState('')
  
  // ==================== STATE - UI ====================
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('')
  
  // ==================== STATE - V2.2: MONITORING BACKEND ====================
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [cadutaRilevata, setCadutaRilevata] = useState(false)
  const [peakPower, setPeakPower] = useState(null)
  const [peakTime, setPeakTime] = useState(null)
  const [monitoringDuration, setMonitoringDuration] = useState(0)
  
  // ==================== EFFECTS ====================
  
  useEffect(() => {
    caricaPresets()
  }, [])
  
  useEffect(() => {
    if (!isMonitoring) return
    const intervalId = setInterval(() => {
      setMonitoringDuration(prev => prev + 100)
    }, 100)
    return () => clearInterval(intervalId)
  }, [isMonitoring])
  
  // ==================== FUNCTIONS ====================
  
  const caricaPresets = async () => {
    try {
      const response = await axios.get(`${API_BASE}/configurations`)
      console.log('📥 Presets caricati:', response.data)
      setPresets(response.data)
    } catch (error) {
      console.error('❌ Errore caricamento presets:', error)
      mostraMessaggio('Errore nel caricamento presets', 'error')
    }
  }
  
  const handlePresetSelect = async (e) => {
    const presetId = e.target.value
    if (!presetId) {
      setCorda('')
      setAssicuratore('')
      setOperatore('')
      setSelectedPreset('')
      return
    }
    try {
      const response = await axios.get(`${API_BASE}/configurations/${presetId}`)
      const config = response.data
      setCorda(config.corda)
      setAssicuratore(config.assicuratore)
      setOperatore(config.operatore)
      setSelectedPreset(presetId)
      mostraMessaggio(`✅ Preset '${config.nome_preset}' caricato`, 'success')
    } catch (error) {
      console.error('❌ Errore caricamento preset:', error)
      mostraMessaggio('Errore nel caricamento preset', 'error')
    }
  }
  
  const handleConferma = async (e) => {
    e.preventDefault()
    if (!corda || !assicuratore || !operatore) {
      mostraMessaggio('❌ Compila tutti i campi!', 'error')
      return
    }
    setLoading(true)
    try {
      const payload = {
        corda,
        assicuratore,
        operatore,
        salva_come_preset: nuovoNomePreset || null
      }
      const response = await axios.post(`${API_BASE}/submit`, payload)
      console.log('✅ Form inviato, backend inizia ascolto sensore:', response.data)
      mostraMessaggio(
        `✅ Configurazione salvata! Backend inizia ascolto sensore...`,
        'success'
      )
      if (nuovoNomePreset) {
        setNuovoNomePreset('')
        caricaPresets()
      }
      setCorda('')
      setAssicuratore('')
      setOperatore('')
      console.log('🔊 BACKEND INIZIA ASCOLTO DEL SENSORE')
      setIsMonitoring(true)
      setCadutaRilevata(false)
      setPeakPower(null)
      setPeakTime(null)
      setMonitoringDuration(0)
      mostraMessaggio(
        '🔴 BACKEND IN ASCOLTO - Effettua la caduta e premi CADUTA EFFETTUATA',
        'success'
      )
    } catch (error) {
      console.error('❌ Errore invio dati:', error)
      mostraMessaggio('❌ Errore nell\'invio dei dati', 'error')
    } finally {
      setLoading(false)
    }
  }
  
  const handleCadutaEffettuata = async () => {
    if (!isMonitoring) {
      mostraMessaggio('❌ Backend non è in ascolto!', 'error')
      return
    }
    console.log('⛔ OPERATORE DICE: HO FATTO LA CADUTA')
    setIsMonitoring(false)
    setCadutaRilevata(true)
    try {
      const response = await axios.post(`${API_BASE}/stop-monitoring`, {
        operatore: operatore,
        durata_ascolto_ms: monitoringDuration
      })
      console.log('📊 Backend ha analizzato i dati:', response.data)
      const caduteData = response.data.analisi_caduta
      if (caduteData) {
        setPeakPower(caduteData.picco_potenza_N)
        setPeakTime(caduteData.timestamp_picco)
        mostraMessaggio(
          `✅ Caduta rilevata! Picco: ${caduteData.picco_potenza_N.toFixed(2)} N (T+${caduteData.offset_ms_dalla_caduta}ms)`,
          'success'
        )
      } else {
        mostraMessaggio('⚠️ Nessuna caduta rilevata nel sensore', 'error')
      }
    } catch (error) {
      console.error('❌ Errore comunicazione backend:', error)
      mostraMessaggio('❌ Errore nella comunicazione con il backend', 'error')
    }
  }
  
  const handleResetMonitoring = () => {
    setIsMonitoring(false)
    setCadutaRilevata(false)
    setPeakPower(null)
    setPeakTime(null)
    setMonitoringDuration(0)
    mostraMessaggio('🔄 Monitoraggio resettato', 'success')
  }
  
  /**
   * V2.2: Download di un file CSV dal backend.
   * Il browser scarica il file grazie all'header Content-Disposition: attachment.
   */
  const handleDownload = (path, label) => {
    const url = `${API_BASE}${path}`
    console.log(`📥 Download: ${url}`)
    window.location.href = url
    mostraMessaggio(`📥 Download di ${label} avviato`, 'success')
  }
  
  const mostraMessaggio = (msg, type) => {
    setMessage(msg)
    setMessageType(type)
    setTimeout(() => setMessage(''), 4000)
  }
  
  const deletePreset = async (presetId) => {
    if (!window.confirm('Elimina questo preset?')) return
    try {
      await axios.delete(`${API_BASE}/configurations/${presetId}`)
      mostraMessaggio('✅ Preset eliminato', 'success')
      caricaPresets()
    } catch (error) {
      console.error('❌ Errore eliminazione:', error)
      mostraMessaggio('❌ Errore eliminazione preset', 'error')
    }
  }
  
  // ==================== RENDER ====================
  
  return (
    <div className="container">
      {/* HEADER */}
      <div className="header">
        <h1>⚙️ MVD2555 Configurator</h1>
        <p>V2.2 - Con monitoraggio caduta da sensore</p>
      </div>
      
      {/* MESSAGE */}
      {message && (
        <div className={`message ${messageType}`}>
          {message}
        </div>
      )}
      
      {/* STATO BACKEND MONITORING */}
      {(isMonitoring || cadutaRilevata) && (
        <div className="monitoring-status">
          <div className={`status-badge ${isMonitoring ? 'listening' : 'completed'}`}>
            {isMonitoring ? '🔴 BACKEND IN ASCOLTO' : '✅ CADUTA RILEVATA'}
          </div>
          <div className="monitoring-info">
            {isMonitoring && (
              <p className="listening-text">
                ⏱️ Ascolto in corso: {(monitoringDuration / 1000).toFixed(1)}s
              </p>
            )}
            {peakPower && (
              <>
                <p><strong>Picco Rilevato:</strong> {peakPower.toFixed(2)} N</p>
                <p><strong>Timestamp:</strong> {peakTime}</p>
              </>
            )}
          </div>
          {cadutaRilevata && (
            <button 
              className="button secondary"
              onClick={handleResetMonitoring}
            >
              🔄 Nuovo Monitoraggio
            </button>
          )}
        </div>
      )}
      
      {/* FORM */}
      <form className="form" onSubmit={handleConferma}>
        <div className="form-group">
          <label htmlFor="preset">📋 Carica Preset</label>
          <select
            id="preset"
            className="input select"
            value={selectedPreset}
            onChange={handlePresetSelect}
          >
            <option value="">-- Seleziona un preset --</option>
            {presets.map(preset => (
              <option key={preset.id} value={preset.id}>
                {preset.nome_preset}
              </option>
            ))}
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="corda">🪢 Corda</label>
          <input
            id="corda"
            type="text"
            className="input"
            placeholder="es. 10mm"
            value={corda}
            onChange={e => setCorda(e.target.value)}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="assicuratore">🔗 Assicuratore</label>
          <input
            id="assicuratore"
            type="text"
            className="input"
            placeholder="es. CAMP"
            value={assicuratore}
            onChange={e => setAssicuratore(e.target.value)}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="operatore">👤 Operatore</label>
          <input
            id="operatore"
            type="text"
            className="input"
            placeholder="Nome operatore"
            value={operatore}
            onChange={e => setOperatore(e.target.value)}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="nuovoPreset">💾 Salva come Preset</label>
          <input
            id="nuovoPreset"
            type="text"
            className="input"
            placeholder="Nome preset (opzionale)"
            value={nuovoNomePreset}
            onChange={e => setNuovoNomePreset(e.target.value)}
          />
          <small>Lascia vuoto se non vuoi salvare come preset</small>
        </div>
        
        <button
          type="submit"
          className="button primary"
          disabled={loading || isMonitoring}
        >
          {loading ? '⏳ Invio...' : '✅ CONFERMA'}
        </button>
      </form>
      
      {/* DIVIDER */}
      <div className="divider">───── CADUTA EFFETTUATA ─────</div>
      
      {/* PULSANTE CADUTA */}
      {isMonitoring && (
        <button
          className="button caduta"
          onClick={handleCadutaEffettuata}
          disabled={!isMonitoring}
        >
          ⛔ HO FATTO LA CADUTA!
        </button>
      )}
      
      {!isMonitoring && !cadutaRilevata && (
        <p className="placeholder-text">
          Compila il form e premi CONFERMA per avviare il monitoraggio del sensore
        </p>
      )}
      
      {/* PRESETS SECTION */}
      {presets.length > 0 && (
        <div className="presets-section">
          <h2>📚 Preset Salvati ({presets.length})</h2>
          <div className="presets-grid">
            {presets.map(preset => (
              <div key={preset.id} className="preset-card">
                <h3>{preset.nome_preset}</h3>
                <p>
                  <strong>Corda:</strong> {preset.corda}
                  <br />
                  <strong>Assicuratore:</strong> {preset.assicuratore}
                  <br />
                  <strong>Operatore:</strong> {preset.operatore}
                </p>
                <small>
                  Creato: {new Date(preset.data_creazione).toLocaleDateString()}
                </small>
                <div style={{ marginTop: '12px', display: 'flex', gap: '8px' }}>
                  <button
                    className="button small"
                    onClick={() => handlePresetSelect({ target: { value: preset.id } })}
                  >
                    📤 Carica
                  </button>
                  <button
                    className="button small danger"
                    onClick={() => deletePreset(preset.id)}
                  >
                    🗑️ Elimina
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* ===== EXPORT SECTION (V2.2) ===== */}
      <div className="export-section">
        <h2>📊 Esporta dati</h2>
        <p className="export-hint">
          Scarica i dati delle cadute in formato CSV (apribile direttamente in Excel).
        </p>
        <div className="export-buttons">
          <button
            type="button"
            className="button export"
            onClick={() => handleDownload('/export/cadute.csv', 'riepilogo')}
          >
            📥 Scarica riepilogo (tutte le cadute)
          </button>
          <button
            type="button"
            className="button export"
            onClick={() => handleDownload('/export/caduta/-1.csv', 'ultima caduta')}
          >
            📈 Scarica ultima caduta (serie temporale)
          </button>
        </div>
      </div>
    </div>
  )
}