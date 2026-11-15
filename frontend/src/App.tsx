import { useState, type FormEvent } from 'react'
import './App.css'

type Person = {
  id: number
  name: string
  country: string
}

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

function App() {
  const [personId, setPersonId] = useState('')
  const [person, setPerson] = useState<Person | null>(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [newName, setNewName] = useState('')
  const [newCountry, setNewCountry] = useState('')
  const [createError, setCreateError] = useState('')
  const [isCreating, setIsCreating] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const id = Number(personId)
    if (!Number.isInteger(id) || id < 1) {
      setPerson(null)
      setError('Enter a valid positive person ID.')
      return
    }

    setIsLoading(true)
    setError('')
    setPerson(null)

    try {
      const response = await fetch(`${apiBaseUrl}/people/${id}`)
      if (response.status === 404) {
        setError(`No person found with ID ${id}.`)
        return
      }
      if (!response.ok) {
        throw new Error(`The server returned an error (${response.status}).`)
      }

      const result: Person = await response.json()
      setPerson(result)
    } catch (requestError) {
      setError(
        requestError instanceof TypeError
          ? 'Could not connect to the API. Make sure the FastAPI server is running.'
          : requestError instanceof Error
            ? requestError.message
            : 'Could not load this person.',
      )
    } finally {
      setIsLoading(false)
    }
  }

  async function handleCreateSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsCreating(true)
    setCreateError('')

    try {
      const response = await fetch(`${apiBaseUrl}/people`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newName, country: newCountry }),
      })
      if (!response.ok) {
        throw new Error(`The server returned an error (${response.status}).`)
      }

      const createdPerson: Person = await response.json()
      setPersonId(String(createdPerson.id))
      setPerson(createdPerson)
      setError('')
      setNewName('')
      setNewCountry('')
      setIsCreateDialogOpen(false)
    } catch (requestError) {
      setCreateError(
        requestError instanceof TypeError
          ? 'Could not connect to the API. Make sure the FastAPI server is running.'
          : requestError instanceof Error
            ? requestError.message
            : 'Could not create this person.',
      )
    } finally {
      setIsCreating(false)
    }
  }

  function openCreateDialog() {
    setCreateError('')
    setIsCreateDialogOpen(true)
  }

  return (
    <main className="page-shell">
      <section className="lookup-card" aria-labelledby="page-title">
        <div className="eyebrow">
          <span className="status-dot" aria-hidden="true" />
          PEOPLE DIRECTORY
        </div>
        <h1 id="page-title">Find a person</h1>
        <p className="intro">
          Enter an ID to look up someone in the directory.
        </p>

        <form className="lookup-form" onSubmit={handleSubmit}>
          <label htmlFor="person-id">Person ID</label>
          <div className="input-row">
            <input
              id="person-id"
              name="personId"
              type="number"
              min="1"
              step="1"
              placeholder="For example, 2"
              value={personId}
              onChange={(event) => setPersonId(event.target.value)}
              required
            />
            <button type="submit" disabled={isLoading}>
              {isLoading ? 'Searching…' : 'Search'}
              {!isLoading && <span aria-hidden="true">→</span>}
            </button>
          </div>
        </form>

        <button
          className="create-entry-button"
          type="button"
          onClick={openCreateDialog}
        >
          Create new entry
        </button>

        <div className="result-area" aria-live="polite" aria-busy={isLoading}>
          {error && <p className="message error-message" role="alert">{error}</p>}
          {isLoading && <p className="message">Looking up person…</p>}
          {person && (
            <div className="person-results">
              <p className="result-heading">PERSON FOUND</p>
              <label className="result-field">
                <span>Name</span>
                <output>{person.name}</output>
              </label>
              <label className="result-field">
                <span>Country</span>
                <output>{person.country}</output>
              </label>
            </div>
          )}
        </div>

        <footer className="card-footer">
          <span>LOOKUP SERVICE</span>
          <span>API · READY</span>
        </footer>
      </section>
      <p className="page-caption">A simple directory lookup</p>
      {isCreateDialogOpen && (
        <div className="dialog-backdrop">
          <section
            className="create-dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="create-dialog-title"
          >
            <p className="eyebrow">NEW DIRECTORY ENTRY</p>
            <h2 id="create-dialog-title">Add a person</h2>
            <p className="dialog-intro">
              The next available ID will be assigned automatically.
            </p>
            <form className="create-form" onSubmit={handleCreateSubmit}>
              <label htmlFor="new-person-name">Name</label>
              <input
                id="new-person-name"
                name="name"
                type="text"
                maxLength={100}
                value={newName}
                onChange={(event) => setNewName(event.target.value)}
                required
              />
              <label htmlFor="new-person-country">Country</label>
              <input
                id="new-person-country"
                name="country"
                type="text"
                maxLength={100}
                value={newCountry}
                onChange={(event) => setNewCountry(event.target.value)}
                required
              />
              {createError && (
                <p className="message error-message" role="alert">
                  {createError}
                </p>
              )}
              <div className="dialog-actions">
                <button
                  className="cancel-button"
                  type="button"
                  onClick={() => setIsCreateDialogOpen(false)}
                  disabled={isCreating}
                >
                  Cancel
                </button>
                <button type="submit" disabled={isCreating}>
                  {isCreating ? 'Creating…' : 'Create entry'}
                </button>
              </div>
            </form>
          </section>
        </div>
      )}
    </main>
  )
}

export default App
