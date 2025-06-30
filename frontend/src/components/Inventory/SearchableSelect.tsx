import React, { useState, useEffect, useRef } from 'react';
import './SearchableSelect.css';

interface Option {
  id: number;
  name: string;
  description?: string;
  subtitle?: string;
}

interface SearchableSelectProps {
  options: Option[];
  selectedId: number | null;
  onSelect: (option: Option | null) => void;
  placeholder: string;
  loading?: boolean;
  onSearch?: (searchTerm: string) => void;
  label: string;
  required?: boolean;
  error?: string;
  disabled?: boolean;
}

const SearchableSelect: React.FC<SearchableSelectProps> = ({
  options,
  selectedId,
  onSelect,
  placeholder,
  loading = false,
  onSearch,
  label,
  required = false,
  error,
  disabled = false
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredOptions, setFilteredOptions] = useState<Option[]>(options);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [lastSearchTerm, setLastSearchTerm] = useState(''); // Track last searched term
  
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  
  const selectedOption = options.find(option => option.id === selectedId);

  useEffect(() => {
    setFilteredOptions(options);
  }, [options]);

  useEffect(() => {
    if (searchTerm) {
      const filtered = options.filter(option =>
        option.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (option.description && option.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (option.subtitle && option.subtitle.toLowerCase().includes(searchTerm.toLowerCase()))
      );
      setFilteredOptions(filtered);
      setHighlightedIndex(-1);
    } else {
      setFilteredOptions(options);
      setHighlightedIndex(-1);
    }
  }, [searchTerm, options]);

  // Improved debounced search with duplicate prevention
  useEffect(() => {
    // Clear existing timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Search if:
    // 1. onSearch function is provided
    // 2. searchTerm is different from last searched term
    // 3. Either searchTerm has minimum length (2 characters) OR searchTerm is empty (to reset search)
    if (onSearch && searchTerm !== lastSearchTerm && (searchTerm.length >= 2 || (searchTerm.length === 0 && lastSearchTerm.length > 0))) {
      debounceTimerRef.current = setTimeout(() => {
        onSearch(searchTerm);
        setLastSearchTerm(searchTerm); // Update last searched term
      }, 400); // 400ms delay
    }

    // Cleanup timer on unmount or dependency change
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [searchTerm, onSearch, lastSearchTerm]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    if (!isOpen) setIsOpen(true);
  };

  const handleInputFocus = () => {
    setIsOpen(true);
  };

  const handleOptionClick = (option: Option) => {
    onSelect(option);
    setIsOpen(false);
    setSearchTerm('');
    setHighlightedIndex(-1);
    setLastSearchTerm(''); // Reset last search term
  };

  const handleClear = () => {
    onSelect(null);
    setSearchTerm('');
    setHighlightedIndex(-1);
    setLastSearchTerm(''); // Reset last search term
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) {
      if (e.key === 'ArrowDown' || e.key === 'Enter') {
        setIsOpen(true);
        e.preventDefault();
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex(prev => 
          prev < filteredOptions.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex(prev => 
          prev > 0 ? prev - 1 : filteredOptions.length - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && filteredOptions[highlightedIndex]) {
          handleOptionClick(filteredOptions[highlightedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setSearchTerm('');
        setHighlightedIndex(-1);
        setLastSearchTerm(''); // Reset last search term
        break;
    }
  };

  return (
    <div className="searchable-select" ref={dropdownRef}>
      <label className="searchable-select-label">
        {label} {required && <span className="required">*</span>}
      </label>
      
      <div className={`searchable-select-container ${error ? 'error' : ''} ${disabled ? 'disabled' : ''}`}>
        <div className="searchable-select-input-wrapper">
          <input
            ref={inputRef}
            type="text"
            className="searchable-select-input"
            placeholder={selectedOption ? selectedOption.name : placeholder}
            value={searchTerm}
            onChange={handleInputChange}
            onFocus={handleInputFocus}
            onKeyDown={handleKeyDown}
            disabled={disabled}
          />
          
          <div className="searchable-select-controls">
            {selectedOption && !disabled && (
              <button
                type="button"
                className="clear-button"
                onClick={handleClear}
                title="Clear selection"
              >
                ×
              </button>
            )}
            <button
              type="button"
              className={`dropdown-arrow ${isOpen ? 'open' : ''}`}
              onClick={() => !disabled && setIsOpen(!isOpen)}
              disabled={disabled}
            >
              ▼
            </button>
          </div>
        </div>

        {isOpen && (
          <div className="searchable-select-dropdown">
            {loading ? (
              <div className="dropdown-loading">Loading...</div>
            ) : filteredOptions.length === 0 ? (
              <div className="dropdown-empty">No options found</div>
            ) : (
              <div className="dropdown-options">
                {filteredOptions.map((option, index) => (
                  <div
                    key={option.id}
                    className={`dropdown-option ${
                      index === highlightedIndex ? 'highlighted' : ''
                    } ${selectedId === option.id ? 'selected' : ''}`}
                    onClick={() => handleOptionClick(option)}
                    onMouseEnter={() => setHighlightedIndex(index)}
                  >
                    <div className="option-name">{option.name}</div>
                    {option.subtitle && (
                      <div className="option-subtitle">{option.subtitle}</div>
                    )}
                    {option.description && (
                      <div className="option-description">{option.description}</div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {error && <div className="searchable-select-error">{error}</div>}
    </div>
  );
};

export default SearchableSelect; 