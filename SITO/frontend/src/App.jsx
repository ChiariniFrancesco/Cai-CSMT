// frontend/src/App.jsx
import React, { useState, useEffect } from 'react'
import axios from 'axios'


const API_BASE = 'http://localhost:8000/api'

export default function App() {
  // ==================== STATE ====================
  
  // Form inputs
  const [corda, setCorda] = useState('')
  const [assicuratore, setAssicuratore] = useState('')
  const [operatore, setOperatore] = useState('')
  
  // Dropdown & Presets
  const [presets, setPresets] = useState([])
  const [selectedPreset, setSelectedPreset] = useState('')
  const [nuovoNomePreset, setNuovoNomePreset] = useState('')
  
  // UI states
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('') // 'success' o 'error'

  // ==================== EFFECTS ====================

  // Carica presets all'avvio
  useEffect(() => {
    caricaPresets()
  }, [])

  // ==================== FUNCTIONS ====================

  /**
   * Carica TUTTI i presets dal server
   * Questi appariranno nel dropdown
   */
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

  /**
   * Quando seleziona un preset dal dropdown
   * Riempie i 3 input con i valori salvati
   */
  const handlePresetSelect = async (e) => {
    const presetId = e.target.value
    
    if (!presetId) {
      // Reset form
      setCorda('')
      setAssicuratore('')
      setOperatore('')
      setSelectedPreset('')
      return
    }

    try {
      const response = await axios.get(`${API_BASE}/configurations/${presetId}`)
      const config = response.data
      
      // Riempie i 3 input con i dati salvati
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

  /**
   * CONFERMA - Invia i 3 form al server
   * Se vuole salvare come preset, include il nome
   */
  const handleConferma = async (e) => {
    e.preventDefault()

    // Validazione
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
        salva_come_preset: nuovoNomePreset || null // Se vuoto, null
      }

      const response = await axios.post(`${API_BASE}/submit`, payload)
      
      console.log('✅ Response dal server:', response.data)

      mostraMessaggio(
        `✅ Configurazione salvata!${nuovoNomePreset ? ` (Preset: ${nuovoNomePreset})` : ''}`,
        'success'
      )

      // Se ha salvato come preset, ricarica la lista
      if (nuovoNomePreset) {
        setNuovoNomePreset('')
        caricaPresets()
      }

      // Reset form
      setCorda('')
      setAssicuratore('')
      setOperatore('')

    } catch (error) {
      console.error('❌ Errore invio dati:', error)
      mostraMessaggio('❌ Errore nell\'invio dei dati', 'error')
    } finally {
      setLoading(false)
    }
  }

  /**
   * Mostra messaggio temporaneo
   */
  const mostraMessaggio = (msg, type) => {
    setMessage(msg)
    setMessageType(type)
    setTimeout(() => setMessage(''), 3000)
  }

  /**
   * Elimina un preset
   */
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
      <header className="header">
        <h1>CAI Mountain Gear Testing ⛰️</h1>
        <p>Gestisci configurazioni con presets salvati</p>
      </header>

      {/* MESSAGE NOTIFICATION */}
      {message && (
        <div className={`message ${messageType}`}>
          {message}
        </div>
      )}

      {/* MAIN FORM */}
      <form className="form" onSubmit={handleConferma}>
        
        {/* DROPDOWN PRESETS */}
        <div className="form-group">
          <label htmlFor="preset">📌 Carrica un Preset Salvato:</label>
          <select
            id="preset"
            value={selectedPreset}
            onChange={handlePresetSelect}
            className="input select"
          >
            <option value="">-- Seleziona un preset --</option>
            {presets.map(preset => (
              <option key={preset.id} value={preset.id}>
                {preset.nome_preset}
              </option>
            ))}
          </select>
        </div>

        {/* DIVIDER */}
        <div className="divider">O COMPILA MANUALMENTE</div>

        {/* INPUT 1: CORDA */}
        <div className="form-group">
          <label htmlFor="corda">Corda Usata:</label>
          <input
            id="corda"
            type="text"
            value={corda}
            onChange={(e) => setCorda(e.target.value)}
            placeholder="es: Corda Dinamica 10mm"
            className="input"
          />
        </div>

        {/* INPUT 2: ASSICURATORE */}
        <div className="form-group">
          <label htmlFor="assicuratore">Assicuratore Usato:</label>
          <input
            id="assicuratore"
            type="text"
            value={assicuratore}
            onChange={(e) => setAssicuratore(e.target.value)}
            placeholder="es: CAMP Dyna-X"
            className="input"
          />
        </div>

        {/* INPUT 3: OPERATORE */}
        <div className="form-group">
          <label htmlFor="operatore">Nome Operatore:</label>
          <input
            id="operatore"
            type="text"
            value={operatore}
            onChange={(e) => setOperatore(e.target.value)}
            placeholder="es: Mario Rossi"
            className="input"
          />
        </div>

        {/* SALVA COME PRESET */}
        <div className="form-group">
          <label htmlFor="nomePreset">💾 Salva come Preset (opzionale):</label>
          <input
            id="nomePreset"
            type="text"
            value={nuovoNomePreset}
            onChange={(e) => setNuovoNomePreset(e.target.value)}
            placeholder="es: Settaggio Arena A"
            className="input"
          />
          <small>Se vuoto, i dati NON saranno memorizzati</small>
        </div>

        {/* BUTTON CONFERMA */}
        <button
          type="submit"
          disabled={loading}
          className="button primary"
        >
          {loading ? '⏳ Invio...' : '✅ CONFERMA'}
        </button>
      </form>

      {/* PRESETS LIST */}
      {presets.length > 0 && (
        <div className="presets-section">
          <h2>📋 Presets Salvati</h2>
          <div className="presets-grid">
            {presets.map(preset => (
              <div key={preset.id} className="preset-card">
                <h3>{preset.nome_preset}</h3>
                <p><strong>Corda:</strong> {preset.corda}</p>
                <p><strong>Assicuratore:</strong> {preset.assicuratore}</p>
                <p><strong>Operatore:</strong> {preset.operatore}</p>
                <small>Creato: {new Date(preset.data_creazione).toLocaleDateString()}</small>
                <button
                  onClick={() => deletePreset(preset.id)}
                  className="button danger small"
                >
                  🗑️ Elimina
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
