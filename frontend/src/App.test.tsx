import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders CSCMS application', () => {
  render(<App />);
  const titleElement = screen.getByText(/CSCMS/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders dashboard page', () => {
  render(<App />);
  const dashboardElements = screen.getAllByText(/Dashboard/i);
  expect(dashboardElements.length).toBeGreaterThan(0);
});

test('renders navigation menu', () => {
  render(<App />);
  const storesElements = screen.getAllByText(/Stores/i);
  const inventoryElements = screen.getAllByText(/Inventory/i);
  const reportsElements = screen.getAllByText(/Reports/i);

  expect(storesElements.length).toBeGreaterThan(0);
  expect(inventoryElements.length).toBeGreaterThan(0);
  expect(reportsElements.length).toBeGreaterThan(0);
});
