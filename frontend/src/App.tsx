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
    </main>
  )
}

export default App
